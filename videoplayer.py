import sys
import os
import vlc
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSlider, QFileDialog, QProgressBar, QDesktopWidget
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QCursor, QIcon

class VideoPlayer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("J.M Video Player")
        self.setGeometry(100, 50, 600, 450)
        self.setWindowIcon(QIcon("play.png"))  # Set window icon

        self.instance = vlc.Instance()
        self.media_player = self.instance.media_player_new()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.central_widget.setLayout(self.layout)

        self.video_widget = QWidget()
        self.layout.addWidget(self.video_widget)

        self.setup_vlc_video_output()

        self.progress_bar_layout = QHBoxLayout()
        self.layout.addLayout(self.progress_bar_layout)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar_layout.addWidget(self.progress_bar)
        self.progress_bar.setStyleSheet("QProgressBar { border-top: 4px solid rgba(0,0,0,0); border-bottom: 4px solid rgba(0,0,0,0); border-radius: 5px; color: rgba(0,0,0,0); background-color: rgba(0,0,0,0.1); height: 1px; }")
        self.progress_bar.mousePressEvent = self.seek

        self.control_layout = QHBoxLayout()
        self.layout.addLayout(self.control_layout)

        self.open_button = QPushButton()
        self.open_button.setIcon(QIcon("open_file.png"))
        self.open_button.clicked.connect(self.open_file)
        self.control_layout.addWidget(self.open_button)
        self.open_button.setFixedWidth(30)
        self.open_button.setFixedHeight(25)

        self.open_folder_button = QPushButton()
        self.open_folder_button.setIcon(QIcon("open_folder.png"))
        self.open_folder_button.clicked.connect(self.open_folder)
        self.control_layout.addWidget(self.open_folder_button)
        self.open_folder_button.setFixedWidth(30)
        self.open_folder_button.setFixedHeight(25)

        self.loop_button = QPushButton()
        self.loop_button.setIcon(QIcon("loop.png"))
        self.loop_button.setCheckable(True)
        self.loop_button.clicked.connect(self.toggle_repeat)
        self.control_layout.addWidget(self.loop_button)
        self.loop_button.setFixedWidth(30)
        self.loop_button.setFixedHeight(25)

        self.full_screen_button = QPushButton()
        self.full_screen_button.setIcon(QIcon("fullscreen.png"))
        self.full_screen_button.clicked.connect(self.toggle_full_screen)
        self.control_layout.addWidget(self.full_screen_button)
        self.full_screen_button.setFixedWidth(30)
        self.full_screen_button.setFixedHeight(25)

        self.previous_button = QPushButton()
        self.previous_button.setIcon(QIcon("previous.png"))
        self.previous_button.clicked.connect(self.play_previous)
        self.control_layout.addWidget(self.previous_button)
        self.previous_button.setFixedWidth(30)
        self.previous_button.setFixedHeight(25)

        self.play_pause_button = QPushButton()
        self.play_pause_button.setIcon(QIcon("play.png"))
        self.play_pause_button.clicked.connect(self.play_pause_video)
        self.control_layout.addWidget(self.play_pause_button)
        self.play_pause_button.setFixedWidth(30)
        self.play_pause_button.setFixedHeight(25)

        self.next_button = QPushButton()
        self.next_button.setIcon(QIcon("next.png"))
        self.next_button.clicked.connect(self.play_next)
        self.control_layout.addWidget(self.next_button)
        self.next_button.setFixedWidth(30)
        self.next_button.setFixedHeight(25)

        self.audio_track_button = QPushButton()
        self.audio_track_button.setIcon(QIcon("audio_track.png"))
        self.audio_track_button.clicked.connect(self.cycle_audio_track)
        self.control_layout.addWidget(self.audio_track_button)
        self.audio_track_button.setFixedWidth(30)
        self.audio_track_button.setFixedHeight(25)

        self.subtitle_track_button = QPushButton()
        self.subtitle_track_button.setIcon(QIcon("subtitle.png"))
        self.subtitle_track_button.clicked.connect(self.cycle_subtitle_track)
        self.control_layout.addWidget(self.subtitle_track_button)
        self.subtitle_track_button.setFixedWidth(30)
        self.subtitle_track_button.setFixedHeight(25)

        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setValue(20)
        self.volume_slider.setFixedWidth(100)
        self.volume_slider.sliderMoved.connect(self.set_volume)
        self.control_layout.addWidget(self.volume_slider)

        self.hide_buttons_timer = QTimer()
        self.hide_buttons_timer.setInterval(1000)  # 1 second
        self.hide_buttons_timer.timeout.connect(self.hide_buttons)

        self.buttons_hidden = False

        self.playlist = []
        self.current_index = -1
        self.repeat_modes = ["Off", "One", "All"]
        self.repeat_mode_index = 0

        # Enable drag and drop
        self.setAcceptDrops(True)

    def setup_vlc_video_output(self):
        if sys.platform.startswith('linux'):  # for Linux using the X Server
            self.media_player.set_xwindow(int(self.video_widget.winId()))
        elif sys.platform == "win32":  # for Windows
            self.media_player.set_hwnd(int(self.video_widget.winId()))
        elif sys.platform == "darwin":  # for MacOS
            self.media_player.set_nsobject(int(self.video_widget.winId()))

        # Set font for subtitles
        self.media_player.video_set_subtitle_file(None)  # Clear any existing subtitle file
        self.media_player.video_set_subtitle_file("Arial")  # Set font to Arial (change to your preferred font)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        files = [url.toLocalFile() for url in event.mimeData().urls()]
        for file_path in files:
            if os.path.isfile(file_path):
                self.playlist.append(file_path)
            elif os.path.isdir(file_path):
                for root, _, files in os.walk(file_path):
                    for file in files:
                        if file.endswith((".mp4", ".avi", ".mkv", ".ts")):
                            self.playlist.append(os.path.join(root, file))
        if self.current_index == -1:
            self.current_index = 0
            self.play_video()

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Video File", "", "Video Files (*.mp4 *.avi *.mkv *.ts)")
        if file_path:
            self.playlist = [file_path]
            self.current_index = 0
            self.play_video()

    def open_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Open Folder")
        if folder_path:
            for root, _, files in os.walk(folder_path):
                for file in files:
                    if file.endswith((".mp4", ".avi", ".mkv", ".ts")):
                        self.playlist.append(os.path.join(root, file))
            if self.playlist:
                self.current_index = 0
                self.play_video()

    def toggle_repeat(self):
        self.repeat_mode_index = (self.repeat_mode_index + 1) % len(self.repeat_modes)
        repeat_mode = self.repeat_modes[self.repeat_mode_index]
        self.loop_button.setIcon(QIcon("loop_off.png"))
        if repeat_mode == "One":
            self.loop_button.setIcon(QIcon("loop_one.png"))
        elif repeat_mode == "All":
            self.loop_button.setIcon(QIcon("loop_all.png"))

    def play_video(self):
        if self.current_index != -1:
            media = self.instance.media_new(self.playlist[self.current_index])
            self.media_player.set_media(media)
            self.media_player.play()
            self.play_pause_button.setIcon(QIcon("pause.png"))  # Change icon to pause

    def play_previous(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.play_video()

    def play_next(self):
        if self.repeat_modes[self.repeat_mode_index] == "One":
            self.current_index = (self.current_index + 1) % len(self.playlist)
            self.play_video()
        elif self.repeat_modes[self.repeat_mode_index] == "All":
            self.current_index = (self.current_index + 1) % len(self.playlist)
            self.play_video()
        elif self.current_index < len(self.playlist) - 1:
            self.current_index += 1
            self.play_video()

    def play_pause_video(self):
        if self.media_player.is_playing():
            self.media_player.pause()
            self.play_pause_button.setIcon(QIcon("play.png"))  # Change icon to play
        else:
            self.media_player.play()
            self.play_pause_button.setIcon(QIcon("pause.png"))  # Change icon to pause

    def set_volume(self, value):
        self.media_player.audio_set_volume(value)

    def update_progress(self):
        media_length = self.media_player.get_length()
        current_time = self.media_player.get_time()
        if media_length > 0:
            self.progress_bar.setRange(0, media_length)
            self.progress_bar.setValue(current_time)

    def seek(self, event):
        position = event.pos().x()
        value = int((position / self.progress_bar.width()) * self.progress_bar.maximum())
        self.media_player.set_time(value)

    def cycle_audio_track(self):
        audio_tracks = self.media_player.audio_get_track_count()
        current_track = self.media_player.audio_get_track()
        next_track = (current_track + 1) % audio_tracks
        self.media_player.audio_set_track(next_track)

    def cycle_subtitle_track(self):
        subtitle_tracks = self.media_player.video_get_spu_count()
        if subtitle_tracks > 0:
            current_track = self.media_player.video_get_spu()
            next_track = (current_track + 1) % subtitle_tracks
            self.media_player.video_set_spu(next_track)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Right:
            self.media_player.set_time(self.media_player.get_time() + 10000)
        elif event.key() == Qt.Key_Left:
            self.media_player.set_time(self.media_player.get_time() - 10000)

    def toggle_full_screen(self):
        if not self.isFullScreen():
            self.showFullScreen()
            self.hide_buttons_timer.start()
            self.hide_buttons()
        else:
            self.showNormal()

    def hide_buttons(self):
        cursor_pos = QCursor.pos()
        screen = QDesktopWidget().screenGeometry()
        distance_from_bottom = screen.height() - cursor_pos.y()

        if self.isFullScreen() and distance_from_bottom > 50:  # Cursor is far from the bottom of the screen
            self.buttons_hidden = True
            self.open_button.hide()
            self.open_folder_button.hide()
            self.loop_button.hide()
            self.full_screen_button.hide()
            self.previous_button.hide()
            self.play_pause_button.hide()
            self.next_button.hide()
            self.audio_track_button.hide()
            self.subtitle_track_button.hide()
            self.volume_slider.hide()
            self.progress_bar.hide()

        elif self.isFullScreen() and self.buttons_hidden:
            self.buttons_hidden = False
            self.progress_bar.show()
            self.open_button.show()
            self.open_folder_button.show()
            self.loop_button.show()
            self.full_screen_button.show()
            self.previous_button.show()
            self.play_pause_button.show()
            self.next_button.show()
            self.audio_track_button.show()
            self.subtitle_track_button.show()
            self.volume_slider.show()

    def mouseMoveEvent(self, event):
        if self.isFullScreen() and not self.buttons_hidden:
            self.hide_buttons_timer.start()
            self.hide_buttons()

    def mousePressEvent(self, event):
        if self.isFullScreen() and not self.buttons_hidden:
            self.hide_buttons_timer.start()
            self.hide_buttons()

def main():
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.show()
    timer = QTimer()
    timer.timeout.connect(player.update_progress)
    timer.start(100)
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

