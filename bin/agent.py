from drpy.cli import cli
from drpy.models import config
from drpy.api.client import Client
from drpy.models.runner import AgentState
from drpy.fsm.states.initialize import Initialize


def main(conf=None):
    """

    :type conf: Config
    :param conf:
    :return:
    """
    drpclient = Client(
        endpoint=conf.endpoint,
        token=conf.token
    )
    agent_state = AgentState(client=drpclient)
    machine_state = Initialize()
    while machine_state.state != "Exit":
        machine_state, agent_state = machine_state.on_event(
            agent_state=agent_state,
            machine_uuid=conf.machine_uuid
        )


if __name__ == "__main__":
    parser = cli.build_arg_parser()
    args = parser.parse_args()
    conf_file = args.conf_file
    if not cli.verify_conf_file(conf_file):
        raise NotImplementedError

    conf = config.parse(conf_file)
    main(conf=conf)
