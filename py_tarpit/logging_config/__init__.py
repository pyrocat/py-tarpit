import queue
import logging
from logging.handlers import QueueHandler, QueueListener
from contextlib import contextmanager


def get_listener():
    que = queue.Queue(-1)
    queue_handler = QueueHandler(que)
    handler = logging.StreamHandler()
    root = logging.getLogger()
    root.addHandler(queue_handler)
    formatter = logging.Formatter('%(threadName)s: %(message)s')
    handler.setFormatter(formatter)
    return QueueListener(que, handler)


@contextmanager
def listener_context():
    listener = get_listener()
    try:
        listener.start()
        yield
    finally:
        listener.stop()