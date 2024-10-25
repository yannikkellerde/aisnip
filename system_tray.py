import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon
from datetime import datetime
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPainter, QPen, QPixmap, QScreen, QColor, QKeySequence
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog, QMainWindow, QShortcut
from util import local_image_to_data_url, AzureModelWrapper
import pyperclip
import keyboard


class SnippingTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        #self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowOpacity(0.1)
        
        screen_geometry = QApplication.primaryScreen().geometry()
        self.setGeometry(screen_geometry)

        self.save_folder = os.path.expanduser("~/Pictures/snips")
        os.makedirs(self.save_folder, exist_ok=True)
        
        self.begin = None
        self.end = None
        
        self.prompt = "Please explain the contents of this image."
        
        self.model = AzureModelWrapper()
        
    def showFullScreen(self) -> None:
        super().showFullScreen()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw the overlay with opacity
        overlay_color = QColor(0, 0, 0, 128)  # Semi-transparent black
        painter.fillRect(self.rect(), overlay_color)

        # If we have a selection, cut it out to reveal the screen content
        if self.begin and self.end:
            rect = QRect(self.begin, self.end)
            painter.setCompositionMode(QPainter.CompositionMode_Clear)
            painter.fillRect(rect, Qt.transparent)

            # Draw a red border around the selection
            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
            painter.setPen(QPen(Qt.red, 2))
            painter.drawRect(rect)
            
    def get_ai_complete(self, img_path):
        data_url = local_image_to_data_url(
            img_path
        )
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": self.prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": data_url,
                        },
                    },
                ],
            }
        ]
        reply = self.model.complete(messages)
        print(reply)
        pyperclip.copy(reply)

    def mousePressEvent(self, event):
        self.begin = event.pos()
        self.end = self.begin
        self.update()

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        self.end = event.pos()
        file_path = self.capture()
        self.begin = self.end = None
        self.close()
        self.get_ai_complete(file_path)

    def capture(self):
        x1 = min(self.begin.x(), self.end.x())
        y1 = min(self.begin.y(), self.end.y())
        x2 = max(self.begin.x(), self.end.x())
        y2 = max(self.begin.y(), self.end.y())
        rect = QRect(x1, y1, x2 - x1, y2 - y1)
        
        screen = QApplication.primaryScreen()
        screenshot = screen.grabWindow(0, rect.x(), rect.y(), rect.width(), rect.height())
        
        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_path = os.path.join(self.save_folder, f"{now}.png")
        screenshot.save(file_path)
        return file_path

app = QApplication(sys.argv)
app.setQuitOnLastWindowClosed(False)

window = SnippingTool()

tray_icon = QSystemTrayIcon(QIcon("clippy.png"))
tray_icon.setToolTip("AI Snip tool")

tray_menu = QMenu()
show_action = QAction("AI Snip")
quit_action = QAction("Quit")
show_action.triggered.connect(window.showFullScreen)
quit_action.triggered.connect(app.quit)

tray_menu.addAction(show_action)
tray_menu.addAction(quit_action)
tray_icon.setContextMenu(tray_menu)

tray_icon.show()

keyboard.add_hotkey('ctrl+shift+a', show_action.trigger)
# window.showFullScreen()

# Adding a keyboard shortcut for the "AI Snip" action
#shortcut = QShortcut(QKeySequence("Ctrl+Shift+A"), window)  # or any preferred key combination
#shortcut.activated.connect(show_action.trigger)

sys.exit(app.exec_())
