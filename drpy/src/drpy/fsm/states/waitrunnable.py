import copy
import logging
import time
import datetime

from drpy.cli import cli
from drpy.exceptions import DRPException, DRPExitException
from drpy.fsm import logger
from drpy.fsm.states.base import BaseState
from drpy.fsm.states.power import Exit, Reboot
from drpy.models import config
from drpy.models.config import ConfigException
from drpy.models.token import Token


class WaitRunnable(BaseState):
    def on_event(self, *args, **kwargs):
        agent_state = kwargs.get("agent_state")
        agent_state = self._check_token(agent_state)
        try:
            machine = self._get_machine(
                agent_state=agent_state,
                machine_uuid=agent_state.machine.Uuid
            )
        except DRPExitException:
            return Exit(), agent_state
        except DRPException:
            agent_state.failed = True
            return WaitRunnable(), agent_state

        if agent_state.machine.BootEnv != machine.BootEnv:
            # The boot env has changed. Time to reboot unless
            # we end in -install and then we exit
            if agent_state.machine.BootEnv.endswith("-install"):
                return Exit(), agent_state
            m_copy = copy.deepcopy(agent_state.machine)
            m_copy.Runnable = False
            self._patch_machine(
                agent_state,
                m_copy
            )
            return Reboot(), agent_state
        agent_state.machine = machine
        if machine.CurrentTask >= len(machine.Tasks):
            if agent_state.runner:
                return Exit(), agent_state
            time.sleep(3)
            return WaitRunnable(), agent_state
        if machine.Runnable:
            logging.debug("Machine Runnable. Checking context. {}".format(
                machine.Context))
            if machine.Context == "":
                from drpy.fsm.states.runtask import RunTask
                return RunTask(), agent_state
        time.sleep(3)
        return WaitRunnable(), agent_state

    def _check_token(self, agent_state):
        logger.debug("Checking if its time to update the api token")
        if agent_state.config.never_update_token:
            logger.debug("Config option never_update_token True. "
                         "Skipping token update.")
            return agent_state
        # check to see if its time to update the token
        # check config last_updated vs duration in mins
        delta = datetime.datetime.now() - agent_state.config.last_updated
        logger.debug("Token last_updated: {}".format(
            agent_state.config.last_updated))
        logger.debug("Token delta: {}".format(delta))
        duration = int(agent_state.config.duration)
        # if (last_updated - now) > timedelta(mins=duration)
        if delta > datetime.timedelta(minutes=duration):
            # grab an updated token
            logger.debug("Attempting to fetch new token.")
            tok_res = agent_state.client.get(
                "machines/{0}/token?ttl=3y".format(
                    agent_state.machine.Uuid
                ))
            logger.debug("New token received. Updating config files.")
            token = Token(**tok_res)
            # update the config files & replace token
            vols = cli.get_volumes(vol_filter="vfat")
            update_dict = {"token": token.Token}
            for vol in vols:
                # we return an update config here each time
                # since its the same config each time we only
                # need to worry about it once.
                logger.debug("Updating config found on volume: {0}".format(
                    vol))
                try:
                    cfg = config.update(replace=update_dict, path=vol)
                    agent_state.config = cfg
                    agent_state.client.setup_token_auth(token=token.Token)
                except ConfigException:
                    log_msg = "Failed to update config file with new info on" \
                              " Volume {}".format(vol)
                    logger.info(log_msg)

        return agent_state
