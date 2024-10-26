from PyQt6.QtWidgets import QApplication, QWidget, QLabel
import sys
from PyQt6.QtCore import Qt, QTimer, QRectF, QPointF, QRect
from PyQt6.QtGui import QPainter, QColor, QFont, QFontMetrics, QPainterPath, QPixmap

class SpeechBubbleWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Speech Bubble")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        
        image_path = "full_clippy.png"

        # Create a QLabel widget to display the image
        self.label = QLabel(self)
        
        # Load the image and set it in the QLabel
        self.pixmap = QPixmap(image_path)
        
        scale_factor = 200/self.pixmap.width()

        self.img_height = int(self.pixmap.height()*scale_factor)
        self.img_width = int(self.pixmap.width()*scale_factor)

        
    def reset(self, text):
        self.full_text = text
        self.displayed_text = ""
        self.char_index = 0
        
        bubble_width = 300 + max(0,min(300, (len(self.full_text) - 100)//2))
        self.resize(bubble_width, 150)

        # Timer for the typewriter effect
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_text)
        self.timer.start(20)  # Adjust the interval as needed (milliseconds)


    def update_text(self):
        # Add one more character each time the timer fires
        if self.char_index < len(self.full_text):
            self.char_index += 1
            self.displayed_text = self.full_text[:self.char_index]
            self.update()  # Trigger a repaint
        else:
            self.timer.stop()  # Stop timer when all characters are displayed

    def paintEvent(self, event):
        # Set the window location to the bottom right corner
        screen_geometry = QApplication.primaryScreen().geometry()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Define bubble color and border
        bubble_color = QColor(252, 250, 207)
        border_color = QColor(0, 0, 0)

        # Set bubble rectangle size and position, convert to QRectF

        font = QFont("Tahoma", 12)
        painter.setFont(font)
        metrics = QFontMetrics(font)
        max_width = self.rect().width() - 60  # Padding for text within bubble

        # Split displayed_text into lines to fit within max_width
        words = [x for x in self.displayed_text.replace("\n", " \n ").split(" ") if x]
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + " " + word if current_line else word
            if word == "\n":
                lines.append(current_line)
                current_line = ""
            elif metrics.horizontalAdvance(test_line) > max_width:
                lines.append(current_line)
                current_line = word  # Start a new line with the current word
            else:
                current_line = test_line  # Add word to the current line

        # Append the last line
        if current_line:
            lines.append(current_line)
            
        line_req = metrics.height() * len(lines)
        self.resize(self.rect().width(), line_req + 90 + self.img_height)

        x = screen_geometry.width() - self.width() - 20
        y = screen_geometry.height() - self.height() - 20
        self.move(x, y)
        painter.drawPixmap(QRect(self.rect().right()-self.img_width,self.rect().bottom()-self.img_height, self.img_width, self.img_height), self.pixmap)

        bubble_rect = QRectF(self.rect().adjusted(20, 20, -20, -50 - self.img_height))

        # Create a path for the bubble with the triangle pointer
        dummy_path = QPainterPath()
        dummy_path.addRoundedRect(bubble_rect, 20, 20)
        points = []
        for i in range(dummy_path.elementCount()):
            element = dummy_path.elementAt(i)
            points.append((element.x, element.y))
        
        # Add the pointer as part of the path to avoid the line
        pointer_top = QPointF(bubble_rect.right() - 110, bubble_rect.bottom())
        pointer_tip = QPointF(bubble_rect.right() - 110, bubble_rect.bottom() + 20)
        pointer_bottom = QPointF(bubble_rect.right() - 100, bubble_rect.bottom())
        
        path = QPainterPath()
        path.moveTo(QPointF(*points[0]))
        
        for point in points[:12]:
            path.lineTo(QPointF(*point))
            
        path.lineTo(pointer_bottom)
        path.lineTo(pointer_tip)
        path.lineTo(pointer_top)
        for point in points[12:]:
            path.lineTo(QPointF(*point))
            
        path.closeSubpath()

        # Draw the combined bubble and pointer shape
        painter.setBrush(bubble_color)
        painter.setPen(border_color)
        painter.drawPath(path)

        # Draw each line of text within the bubble
        painter.setPen(Qt.GlobalColor.black)
        y_offset = 10  # Vertical padding inside the bubble
        line_height = metrics.height()

        for i, line in enumerate(lines):
            painter.drawText(bubble_rect.adjusted(10, y_offset, 0, 0), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop, line)
            y_offset += line_height  # Move down for the next line
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape or event.key() == Qt.Key.Key_Q:
            self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    text = """Hello! This is a seamless speech bubble.
It can contain multiple lines of text and will automatically wrap to fit within the bubble.
The bubble is also resizable based on the text content.
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat."""
    window = SpeechBubbleWidget()
    window.show()
    window.reset(text)
    sys.exit(app.exec())