import logging

from contextlib import contextmanager
from PyQt5.QtCore import QObject, QThreadPool, QMutex

from .actor import Actor

logger = logging.getLogger(__name__)


class ActorSystem(QObject):

    def __init__(self) -> None:
        super().__init__()

        self.__mutex = QMutex()
        self.__is_running = False

        self.__actors = {}
        self.__running = {}
        self.__thread_pool = QThreadPool()

    def create_actor(self, actor_class: type, *nargs, **kwargs):
        with self.__lock():
            actor = actor_class(self, *nargs, **kwargs)

            if actor.name not in self.__actors:
                self.__actors[actor.name] = actor
            else:
                # TODO handle this case, stop old actor, etc
                pass

            if self.__is_running:
                self.__start_actor(actor)

            return actor

    def _remove_actor(self, actor) -> None:
        self.__actors.pop(actor.name, None)
        self.__running.pop(actor.name, None)

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
            for actor in self.__actors.values():
                self.__start_actor(actor)

    def __start_actor(self, actor: Actor) -> None:
        if actor.name not in self.__running:
            logger.info('Starting actor {!r}'.format(actor))
            self.__thread_pool.start(actor)
            self.__running[actor.name] = actor

    def _send(self, receiver: Actor, message, sender: Actor = None) -> None:
        if receiver.name in self.__running:
            receiver._receive(message, sender)
        else:
            raise RuntimeError('Actor {!r} is not running.'.format(self.receiver.name))
