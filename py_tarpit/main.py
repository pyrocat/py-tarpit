import asyncio
import random
import argparse
import logging
from datetime import datetime
from typing import NamedTuple

from logging_config import listener_context


logger = logging.getLogger("asyncio")
logger.setLevel(logging.DEBUG)

INITIAL_HTTP_RESPONSE = b'HTTP/1.1 200 OK\r\n'


class Tarred(NamedTuple):
    addr: str
    time_spent: int
    when: datetime

_tarpit_inhabitants: list[Tarred] = []

def parse_arguments():
    parser = argparse.ArgumentParser(description="Python script for accepting command line arguments.")

    # Add `--port` argument
    parser.add_argument('--port', type=int, help="Specify the port number.")

    args = parser.parse_args()
    return args


async def handler(_reader, writer):
    writer.write(INITIAL_HTTP_RESPONSE)
    addr = writer.get_extra_info('peername')
    _now = datetime.utcnow()
    logger.debug(f"New connection from: {addr} at {datetime.utcnow()}")
    logger.info(f"Total connections so far: {len(_tarpit_inhabitants)}")

    try:
        while True:
            await asyncio.sleep(5)
            header = random.randint(0, 2**32)
            value = random.randint(0, 2**32)
            writer.write(b"X-%x: %x\r\n" % (header, value))
            await writer.drain()
    except ConnectionResetError:
        time_spent = datetime.utcnow() - _now
        _tarpit_inhabitants.append(Tarred(addr=addr, time_spent=time_spent, when=_now))

        most_tarred = max(_tarpit_inhabitants, key=lambda tarred:tarred.time_spent)

        logger.debug(f"Connection from {addr} was reset. Time spent in tarpit: "
                     f"{time_spent}. Leader: {most_tarred.addr} "
                     f"spent in tar pit {most_tarred.time_spent} started "
                     f"from {most_tarred.when.strftime('%m/%d/%Y, %H:%M:%S')}")

    except KeyboardInterrupt:
        raise

async def main():
    args = parse_arguments()
    server = await asyncio.start_server(handler, '0.0.0.0', args.port)
    with listener_context():
        async with server:
            try:
                await server.serve_forever()
            except KeyboardInterrupt:
                logger.info("Shutting down")
                return


if __name__ == "__main__":
    asyncio.run(main())




