#!/usr/bin/env python
import logging
import signal
import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QDesktopWidget, QWidget, QVBoxLayout, \
    QPushButton, QTextEdit
from PyQt5.QtCore import Qt, QTimer

from qt_actor.actor import Actor
from qt_actor.messages import Stop
from qt_actor.system import ActorSystem

root = logging.getLogger()
root.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(levelname)s %(name)s - %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)

logger = logging.getLogger(__name__)


class EchoWidget(QWidget):

    def __init__(self, echo_actor: Actor) -> None:
        super().__init__()


class Gui(QMainWindow):

    def __init__(self, echo_actor: Actor) -> None:
        super().__init__()

        self.echo_actor = echo_actor

        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)

        layout = QVBoxLayout()
        self.main_widget.setLayout(layout)

        self.text_edit = QTextEdit()
        layout.addWidget(self.text_edit)

        button = QPushButton('Send')
        button.clicked.connect(self.on_send)
        layout.addWidget(button)

        screen = QDesktopWidget().screenGeometry()
        self.resize(screen.width(), screen.height())
        self.show()

    def on_send(self) -> None:
        text = self.text_edit.toPlainText()
        if not text:
            return
        self.text_edit.clear()
        self.echo_actor.send(text)


class EchoActor(Actor):

    def __init__(self, actor_system, quit_actor, *nargs, **kwargs) -> None:
        super().__init__(actor_system, *nargs, **kwargs)
        self.__quit_actor = quit_actor

    def act(self, message, sender) -> None:
        if message is Stop:
            logger.info('>>>> Stopping.')
        else:
            if message == 'STOP':
                self.send(Stop)
                self.__quit_actor.send(None)

            logger.info('>>>> {}'.format(message))


class QuitActor(Actor):

    def __init__(self, actor_system, app, *nargs, **kwargs) -> None:
        super().__init__(actor_system, *nargs, **kwargs)
        self.__app = app

    def act(self, message, sender) -> None:
        self.send(Stop)
        self.__app.quit()


def handle_signals(app) -> None:
    def signal_handler(*nargs) -> None:
        app.quit()

    for sig in [signal.SIGINT, signal.SIGTERM]:
        signal.signal(sig, signal_handler)


def main() -> None:
    app = QApplication([])
    app.setApplicationName('Simple Example')
    app.setAttribute(Qt.AA_UseHighDpiPixmaps)

    system = ActorSystem()
    quit_actor = system.create_actor(QuitActor, app, actor_name='quit')
    echo_actor = system.create_actor(EchoActor, quit_actor, actor_name='echo')

    gui = Gui(echo_actor) # noqa

    handle_signals(app)
    timer = QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    system.start()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
