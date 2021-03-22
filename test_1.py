import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


class MyWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.b1 = QPushButton('Next Image')
        self.b2 = QPushButton('Crop')
        self.b3 = QPushButton('Clear')

        self.view = GraphicsView()
        h_box = QHBoxLayout()
        v_box = QVBoxLayout()
        v_box.addWidget(self.b1)
        v_box.addWidget(self.b2)
        v_box.addWidget(self.b3)
        h_box.addWidget(self.view)
        h_box.addLayout(v_box)
        self.setLayout(h_box)
        #self.resize(800, 800)
        self.setWindowTitle("Super Duper Cropper")

        self.show()

class GraphicsView(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.setScene(QGraphicsScene())
        self.item = QGraphicsPixmapItem(QPixmap('landscape.jpg'))
        self.scene().addItem(self.item)
        self.rect_item = QGraphicsRectItem(QRectF(), self.item)
        self.rect_item.setPen(QPen(QColor(51, 153, 255), 2, Qt.SolidLine))
        self.rect_item.setBrush(QBrush(QColor(0, 255, 0, 40)))

    def mousePressEvent(self, event):
        self.pi = self.mapToScene(event.pos())
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        pf = self.mapToScene(event.pos())
        if (self.pi - pf).manhattanLength() > QApplication.startDragDistance():
            self.pf = pf
            self.draw_rect()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        pf = self.mapToScene(event.pos())
        if (self.pi - pf).manhattanLength() > QApplication.startDragDistance():
            self.pf = pf
            self.draw_rect()
        super().mouseReleaseEvent(event)

    def draw_rect(self):
        r = QRectF(self.pi, self.pf).normalized()
        r = self.rect_item.mapFromScene(r).boundingRect()
        self.rect_item.setRect(r)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWidget()
    window.show()
    sys.exit(app.exec_())
