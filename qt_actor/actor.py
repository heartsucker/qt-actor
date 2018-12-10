import logging

from PyQt5.QtCore import QRunnable
from uuid import uuid4

from .messages import Stop

logger = logging.getLogger(__name__)


class Actor(QRunnable):

    def __init__(self, actor_system, *nargs, **kwargs) -> None:
        super().__init__()
        self.setAutoDelete(False)  # required by Qt

        self.__system = actor_system
        self.__inbox = []

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

    def act(self, message, sender=None) -> None:
        raise NotImplementedError

    def _receive(self, message, sender) -> None:
        logger.info('Receiving message {!r} from {!r}'.format(message, sender))
        self.__inbox.append((message, sender))

    def send(self, message, sender=None) -> None:
        logger.info('Message {!r} being sent to {!r} from {!r}'.format(message, self, sender))
        self.__system._send(self, message, sender)

    def run(self) -> None:
        while True:
            if self.__inbox:
                try:
                    message, sender = self.__inbox.pop()
                    logger.debug('{!r}: Processing message {!r} from {!r}.'
                                 .format(self, message, sender))
                    self.act(message, sender)

                    if message is Stop:
                        self.__system._remove_actor(self)
                        return
                except Exception as e:
                    logger.error('Exception thrown: {}'.format(e))

    def __repr__(self) -> str:
        return '<Actor {}>'.format(self.name)
