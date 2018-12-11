import logging

from PyQt5.QtCore import QRunnable
from uuid import uuid4

from .messages import Stop

logger = logging.getLogger(__name__)


class Actor(QRunnable):

    def __init__(self, actor_system, *nargs, **kwargs) -> None:
        super().__init__()
        self.setAutoDelete(False)  # required by Qt

        self.__is_running = False
        self.__is_stopped = False
        self.__run_call_count = 0
        self.__system = actor_system
        self.__inbox = []
        self.__actors = {}

        actor_name = kwargs.pop('actor_name', None)
        if actor_name is None:
            actor_name = uuid4()
        self.__name = str(actor_name)

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self) -> None:
        raise AttributeError("'name' is read only.")

    @name.deleter
    def name(self) -> None:
        raise AttributeError("'name' is read only.")

    @property
    def is_running(self) -> str:
        return self.__is_running

    @is_running.setter
    def is_running(self) -> None:
        raise AttributeError("'is_running' is read only.")

    @is_running.deleter
    def is_running(self) -> None:
        raise AttributeError("'is_running' is read only.")

    def act(self, message, sender=None) -> None:
        raise NotImplementedError

    def _receive(self, message, sender) -> None:
        logger.info('Receiving message {!r} from {!r}'.format(message, sender))
        self.__inbox.append((message, sender))

    def send(self, message, sender=None) -> None:
        logger.info('Message {!r} being sent to {!r} from {!r}'.format(message, self, sender))
        self.__system._send(self, message, sender)

    def create_actor(self, actor_class: type, *nargs, **kwargs):
        actor = self.__system.create_actor(actor_class, *nargs, **kwargs)
        self.__actors[actor.name] = actor
        return actor

    def remove_actor(self, actor):
        self.__actors.pop(actor.name, None)
        actor.send(Stop)

    def run(self) -> None:
        self.__run_call_count += 1

        # if this thread is already running somewhere else, exit and let the other do the work
        if self.__is_running:
            return

        self.__is_running = True
        while self.__run_call_count and not self.__is_stopped:
            if self.__inbox:
                try:
                    message, sender = self.__inbox.pop()
                    logger.debug('{!r}: Processing message {!r} from {!r}.'
                                 .format(self, message, sender))
                    self.act(message, sender)

                    if message is Stop:
                        for actor in self.__actors.values():
                            actor.send(Stop)
                        self.__system._remove_actor(self)
                        self.__is_stopped = True
                        break
                except Exception as e:
                    logger.error('Exception thrown: {}'.format(e))
            else:
                self.__run_call_count -= 1
        self.__is_running = False

    def __repr__(self) -> str:
        return '<Actor {}>'.format(self.name)
