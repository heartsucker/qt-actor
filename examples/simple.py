#!/usr/bin/env python
import logging
import signal
import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QDesktopWidget, QWidget, QVBoxLayout, \
    QScrollArea, QHBoxLayout, QPushButton, QTextEdit
from PyQt5.QtCore import Qt, QTimer

from qt_actor.actor import Actor
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

    def add_text(self, text: str) -> None:
        pass


class EchoActor(Actor):

    def __init__(self, *nargs, **kwargs) -> None:
        super().__init__(*nargs, **kwargs)

    def act(self, message, sender) -> None:
        logger.info('>>>> {}'.format(message))


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
    echo_actor = system.create_actor(EchoActor, actor_name='echo')

    gui = Gui(echo_actor)

    handle_signals(app)
    timer = QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    system.start()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
