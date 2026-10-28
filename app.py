"""PC Diagnostic: local, bounded prank. No hardware diagnostics are performed."""
import sys
import tempfile
from pathlib import Path

from PySide6.QtCore import QEvent, QObject, QThread, QTimer, Qt, QUrl, Signal
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtWidgets import (
    QApplication, QComboBox, QLabel, QProgressBar, QPushButton,
    QVBoxLayout, QWidget,
)
from media import decrypt


class Prepare(QThread):
    ready = Signal(str)
    failed = Signal(str)

    def __init__(self, destination):
        super().__init__()
        self.destination = destination

    def run(self):
        try:
            if getattr(sys, 'frozen', False):
                from media_key import KEY
                root = Path(sys._MEIPASS)
                data = decrypt((root / 'media.bin').read_bytes(), KEY)
                self.destination.write_bytes(data)
                self.ready.emit(str(self.destination))
            else:
                video = Path(__file__).resolve().parent / 'bad-apple.mp4'
                if not video.is_file():
                    raise FileNotFoundError('Adicione bad-apple.mp4 à pasta do projeto.')
                self.ready.emit(str(video))
        except Exception as exc:
            self.failed.emit('Não foi possível preparar o vídeo: ' + str(exc))


class VideoWindow(QWidget):
    def __init__(self, controller, path, index):
        super().__init__()
        self.controller = controller
        self.setWindowTitle('Bad Apple — Esc para sair')
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        video = QVideoWidget()
        layout.addWidget(video)
        self.player = QMediaPlayer(self)
        self.audio = QAudioOutput(self)
        self.audio.setVolume(0.35 if index == 0 else 0.0)
        self.player.setAudioOutput(self.audio)
        self.player.setVideoOutput(video)
        self.player.setLoops(QMediaPlayer.Loops.Infinite)
        self.player.errorOccurred.connect(
            lambda *_: controller.status.setText(
                'Falha na reprodução. Use MP4 H.264/AAC. Esc para encerrar.'))
        self.player.setSource(QUrl.fromLocalFile(path))
        area = QApplication.primaryScreen().availableGeometry()
        width, height = min(420, area.width() * 2 // 3), min(320, area.height() * 2 // 3)
        self.setGeometry(
            area.x() + (area.width() - width) * (index % 3) // 2,
            area.y() + (area.height() - height) * (index // 3), width, height)

    def closeEvent(self, event):
        event.accept()
        self.controller.stop()


class EscapeFilter(QObject):
    def __init__(self, controller):
        super().__init__(controller)
        self.controller = controller

    def eventFilter(self, watched, event):
        if event.type() == QEvent.Type.KeyPress and event.key() == Qt.Key.Key_Escape:
            self.controller.stop()
            return True
        return False


class Diagnostic(QWidget):
    def __init__(self):
        super().__init__()
        self.stopping = False
        self.windows = []
        self.worker = None
        self.temp = tempfile.TemporaryDirectory(prefix='PcDiagnostic-')
        self.setWindowTitle('PC Diagnostic')
        self.setFixedSize(540, 380)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        title = QLabel('PC Diagnostic')
        title.setStyleSheet('font-size: 28px; font-weight: bold')
        layout.addWidget(title)
        layout.addWidget(QLabel('Selecione um componente para iniciar a análise.'))
        self.component = QComboBox()
        self.component.addItems(['Processador', 'Memória RAM', 'Placa de vídeo', 'Armazenamento'])
        layout.addWidget(self.component)
        self.start = QPushButton('Iniciar diagnóstico')
        self.start.clicked.connect(self.diagnose)
        layout.addWidget(self.start)
        self.progress = QProgressBar()
        self.progress.setValue(0)
        layout.addWidget(self.progress)
        self.status = QLabel('Pronto para iniciar')
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        self.timer = QTimer(self)
        self.timer.setInterval(115)
        self.timer.timeout.connect(self.advance)
        self.deadline = QTimer(self)
        self.deadline.setSingleShot(True)
        self.deadline.timeout.connect(self.stop)
        self.spawn_timer = QTimer(self)
        self.spawn_timer.setInterval(220)
        self.spawn_timer.timeout.connect(self.spawn)
        self.escape_filter = EscapeFilter(self)
        QApplication.instance().installEventFilter(self.escape_filter)
        QApplication.instance().aboutToQuit.connect(self.cleanup)

    def diagnose(self):
        self.start.setEnabled(False)
        self.component.setEnabled(False)
        self.progress.setRange(0, 0)
        self.status.setText('Preparando análise de ' + self.component.currentText() + '…')
        self.worker = Prepare(Path(self.temp.name) / 'playback.mp4')
        self.worker.ready.connect(self.prepared)
        self.worker.failed.connect(self.failed)
        self.worker.start()

    def prepared(self, path):
        if self.stopping:
            return
        self.path = path
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.timer.start()

    def failed(self, message):
        if self.stopping:
            return
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.status.setText(message)
        self.start.setText('Encerrar')
        self.start.clicked.disconnect()
        self.start.clicked.connect(self.stop)
        self.start.setEnabled(True)

    def advance(self):
        value = self.progress.value() + 3
        self.progress.setValue(value)
        self.status.setText(f'Verificando componentes… {value}%')
        if value >= 78:
            self.timer.stop()
            self.setWindowTitle('Alerta do sistema')
            self.status.setStyleSheet('color: #b42318; font-weight: bold')
            self.status.setText(
                'SISTEMA HACKEADO E COMPROMETIDO!\n\n'
                'Pegadinha :) Nenhuma invasão aconteceu.\n'
                'Esc ou fechar qualquer janela encerra tudo.')
            self.deadline.start(45_000)
            self.spawn()
            self.spawn_timer.start()

    def spawn(self):
        if self.stopping or len(self.windows) >= 6:
            self.spawn_timer.stop()
            return
        window = VideoWindow(self, self.path, len(self.windows))
        self.windows.append(window)
        window.show()
        window.player.play()

    def stop(self):
        if self.stopping:
            return
        self.stopping = True
        self.timer.stop()
        self.spawn_timer.stop()
        self.deadline.stop()
        for window in self.windows:
            window.player.stop()
            window.player.setSource(QUrl())
            window.close()
        QApplication.instance().quit()

    def cleanup(self):
        # The worker never touches UI; wait for its file handles before deletion.
        if self.worker is not None:
            self.worker.wait()
        try:
            self.temp.cleanup()
        except OSError:
            # A forced shutdown or a decoder holding a handle can leave this directory.
            pass

    def closeEvent(self, event):
        event.accept()
        self.stop()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName('PC Diagnostic')
    window = Diagnostic()
    window.show()
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
