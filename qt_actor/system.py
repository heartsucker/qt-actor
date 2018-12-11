import logging

from contextlib import contextmanager
from PyQt5.QtCore import QObject, QThreadPool, QMutex

from .actor import Actor
from .messages import Stop

logger = logging.getLogger(__name__)


class ActorSystem(QObject):

    def __init__(self) -> None:
        super().__init__()

        self.__mutex = QMutex()
        self.__is_running = False
        self.__actors = {}
        self.__thread_pool = QThreadPool()

    def create_actor(self, actor_class: type, *nargs, **kwargs):
        with self.__lock():
            actor = actor_class(self, *nargs, **kwargs)

            if actor.name not in self.__actors:
                self.__actors[actor.name] = actor
            else:
                # TODO handle this case, stop old actor, etc
                pass

            return actor

    def _remove_actor(self, actor) -> None:
        self.__actors.pop(actor.name, None)

    @contextmanager
    def __lock(self) -> None:
        while True:
            if self.__mutex.tryLock():
                break
        try:
            yield
        finally:
            self.__mutex.unlock()

    def start(self) -> None:
        logger.info('Starting system.')
        with self.__lock():
            self.__is_running = True

    def stop(self) -> None:
        for actor in list(self.__actors.values()):
            self._send(actor, Stop)

        while self.__actors:
            pass

    def _send(self, receiver: Actor, message, sender: Actor = None) -> None:
        if receiver.name in self.__actors:
            receiver._receive(message, sender)
            self.__thread_pool.start(receiver)
