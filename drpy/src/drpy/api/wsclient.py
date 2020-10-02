import asyncio
import json
import logging
import ssl
import websockets

from urllib.parse import urlparse


ctx = ssl.create_default_context()
ctx.set_ecdh_curve("secp384r1")
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


async def wait_for_update(token=None, uri=None, machine=None):
    """
    Given a token, uri, and machine number open a websocket
    connection to uri and wait for save & update events for
    machine. Returns a Machine

    :param token:
    :param uri:
    :param machine:
    :return:
    """
    if "http" in uri:
        uri = urlparse(uri).netloc
    async with websockets.connect(
            'wss://{0}/api/v3/ws?token={1}'.format(
                uri, token), ssl=ctx) as websocket:
        try:
            # update & save
            save = "register machines.save.{}".format(machine)
            update = "register machines.update.{}".format(machine)
            logging.debug("Registering for WSS Events.")
            logging.debug("Registration for saves: {}".format(save))
            logging.debug("Registration for updates: {}".format(update))
            await websocket.send(save)
            save_res = await asyncio.wait_for(websocket.recv(), None)
            logging.debug("Server Sent Save Reg: {}".format(
                json.loads(save_res)))
            await websocket.send(update)
            update_res = await asyncio.wait_for(websocket.recv(), None)
            logging.debug("Server Sent Update Reg: {}".format(
                json.loads(update_res)))
            while True:
                logging.debug("Waiting on machine event from server.")
                msg_res = await asyncio.wait_for(websocket.recv(), None)
                msg = json.loads(msg_res)
                logging.debug("Server Sent Machine: {}".format(msg))
                break

        finally:
            logging.debug("Closing websocket.")
            await websocket.close()
            return True
