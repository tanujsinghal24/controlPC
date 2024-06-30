from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QGraphicsDropShadowEffect
from PyQt5.QtCore import Qt, QPoint, QRect, QTimer
from PyQt5.QtGui import QColor, QPainter, QBrush, QPolygon
import sys
import multiprocessing
import threading


class ToolTip(QWidget):
    def __init__(self, text="", parent=None, width=200):
        super().__init__(parent, Qt.ToolTip)
        self.setWindowFlags(Qt.ToolTip | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.setStyleSheet("""
            QWidget {
                background-color: #333333;
                color: white;
                border-radius: 16px;
                font-family: Arial;
                font-size: 14px;
            }
            QLabel {
                background-color: #333333;
                color: white;
                border-radius: 16px;
                padding: 10px; 
                font-family: Arial;
                font-size: 16px;
            }
        """)

        layout = QVBoxLayout(self)
        self.label = QLabel(text, self)
        self.label.setWordWrap(True)
        self.label.setFixedWidth(width)
        layout.addWidget(self.label)
        self.setLayout(layout)

        self.shadow_effect = QGraphicsDropShadowEffect(self)
        self.shadow_effect.setBlurRadius(20)
        self.shadow_effect.setOffset(0, 0)
        self.shadow_effect.setColor(QColor(0, 0, 0, 160))
        self.setGraphicsEffect(self.shadow_effect)

    def show_tooltip(self, pos: QPoint, text: str):
        self.label.setText(text)
        self.adjustSize()
        self.move(pos)
        self.show()

    def hide_tooltip(self):
        self.hide()

    def update_tooltip(self, text: str, pos: QPoint = None, width: int = None):
        self.label.setText(text)
        if width:
            self.label.setFixedWidth(width)
        self.adjustSize()
        if pos:
            self.move(pos)
        self.show()

    def destroy_tooltip(self):
        self.close()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        # Draw the arrow tip
        arrow_height = 15
        arrow_width = 30
        center_x = self.width() // 2
        arrow_tip = QPoint(center_x, 0)
        left_base = QPoint(center_x - arrow_width // 2, arrow_height + 5)
        right_base = QPoint(center_x + arrow_width // 2, arrow_height + 5)

        points = [arrow_tip, left_base, right_base]
        painter.setBrush(QBrush(QColor(51, 51, 51, 220)))
        painter.setPen(Qt.NoPen)
        painter.drawPolygon(QPolygon(points))


def ui_listener(queue):
    print("tooltip ui process has begun")
    app = QApplication(sys.argv)
    app.processEvents()  # Ensure all events are processed
    tooltip = ToolTip("Initial Tooltip", width=250)
    # tooltip.show_tooltip(QPoint(100, 100), "Waiting for OCR results...")
    timer = QTimer()

    def update_tooltip(text, pos):
        for screen in app.screens():
            print(screen.geometry())
        print("tooltip update invoked")
        tooltip.update_tooltip(text, QPoint(pos[0]-125, pos[1]+10), 250)

    def process_queue():
        while not queue.empty():
            event = queue.get()
            print("hit")
            eventType, arg = event
            if eventType == 'OCR_RES':
                text, pos = arg
                print(pos)
                print("positon passed is printed here")
                update_tooltip(text, pos)
            elif eventType == "QUIT":
                print("end of ui process")
                timer.stop()
                timer.disconnect()
                app.quit()


    timer.timeout.connect(process_queue)
    timer.start(100)
    sys.exit(app.exec_())

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     tooltip = ToolTip("Initial Tooltip", width=250)
#     tooltip.show_tooltip(QPoint(300, 300), "Enhanced Tooltip with Fixed Width and Shadow")
#     sys.exit(app.exec_())
