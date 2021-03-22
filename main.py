import sys
import cv2
import numpy as np
import qimage2ndarray
from copy import deepcopy
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from scripts import Images

class Filter(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui\\filter_frame.ui", self)
        self.frame = self.findChild(QFrame, "frame")
        self.contrast_btn = self.findChild(QPushButton, "contrast_btn")
        self.sharpen_btn = self.findChild(QPushButton, "sharpen_btn")
        self.cartoon_btn = self.findChild(QPushButton, "cartoon_btn")
        self.cartoon_btn1 = self.findChild(QPushButton, "cartoon_btn2")
        self.invert_btn = self.findChild(QPushButton, "invert_btn")

        self.y_btn = self.findChild(QPushButton, "y_btn")
        self.y_btn.setIcon(QIcon("icon/check.png"))
        self.n_btn = self.findChild(QPushButton, "n_btn")
        self.n_btn.setIcon(QIcon("icon/cross.png"))

class Adjust(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui\\adjust_frame.ui", self)
        self.frame = self.findChild(QFrame, "frame")
        self.crop_btn = self.findChild(QPushButton, "crop_btn")
        self.rotate_btn = self.findChild(QPushButton, "rotate_btn")
        self.brightness_btn = self.findChild(QPushButton, "brightness_btn")
        self.contrast_btn = self.findChild(QPushButton, "contrast_btn")
        self.saturation_btn = self.findChild(QPushButton, "saturation_btn")
        self.mask_btn = self.findChild(QPushButton, "mask_btn")

        self.y_btn = self.findChild(QPushButton, "y_btn")
        self.y_btn.setIcon(QIcon("icon/check.png"))
        self.n_btn = self.findChild(QPushButton, "n_btn")
        self.n_btn.setIcon(QIcon("icon/cross.png"))

class Crop(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui\\crop_btn.ui", self)
        self.frame = self.findChild(QFrame, "frame")
        self.y_btn = self.findChild(QPushButton, "y_btn")
        self.y_btn.setIcon(QIcon("icon/check.png"))
        self.n_btn = self.findChild(QPushButton, "n_btn")
        self.n_btn.setIcon(QIcon("icon/cross.png"))
        self.slider = self.findChild(QSlider, "slider")


class ResizableRubberBand(QWidget):
    def __init__(self, parent=None, img_class=None, update=None):
        super(ResizableRubberBand, self).__init__(parent)
        self.img_class, self.update = img_class, update
        self.draggable, self.mousePressPos, self.mouseMovePos = True, None, None
        self.left, self.right, self.top, self.bottom = None, None, None, None
        self.borderRadius = 0

        self.setWindowFlags(Qt.SubWindow)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(QSizeGrip(self), 0, Qt.AlignLeft | Qt.AlignTop)
        layout.addWidget(QSizeGrip(self), 0, Qt.AlignRight | Qt.AlignBottom)

        self._band = QRubberBand(QRubberBand.Rectangle, self)

        self._band.show()
        self.show()

    def update_dim(self):
        try:
            self.left, self.top = self.pos().x(), self.pos().y()
            self.right, self.bottom = self._band.width() + self.left, self._band.height() + self.top
        except:
            pass

    def resizeEvent(self, event):
        try:
            self.left, self.top = self.pos().x(), self.pos().y()
            self.right, self.bottom = self._band.width() + self.left, self._band.height() + self.top
        except:
            pass
        self._band.resize(self.size())

    def paintEvent(self, event):
        # Get current window size
        window_size = self.size()
        qp = QPainter(self)
        qp.drawRoundedRect(0, 0, window_size.width(), window_size.height(), self.borderRadius, self.borderRadius)

    def mousePressEvent(self, event):
        if self.draggable and event.button() == Qt.LeftButton:

            self.mousePressPos = event.globalPos()  # global
            self.mouseMovePos = event.globalPos() - self.pos()  # local

    def mouseMoveEvent(self, event):
        if self.draggable and event.buttons() & Qt.LeftButton:
            if self.right <= self.img_class.img_width and self.bottom <= self.img_class.img_height \
                    and self.left >= 0 and self.top >= 0:
                globalPos = event.globalPos()
                diff = globalPos - self.mouseMovePos
                self.move(diff)  # move window
                self.mouseMovePos = globalPos - self.pos()

            self.left, self.top = self.pos().x(), self.pos().y()
            self.right, self.bottom = self._band.width() + self.left, self._band.height() + self.top

    def mouseReleaseEvent(self, event):
        if self.mousePressPos is not None:
            if event.button() == Qt.LeftButton:
                self.mousePressPos = None

        if self.left < 0:
            self.left = 0
            self.move(0, self.top)
        if self.right > self.img_class.img_width:
            self.left = self.img_class.img_width - self._band.width()
            self.move(self.left, self.top)
        if self.bottom > self.img_class.img_height:
            self.top = self.img_class.img_height - self._band.height()
            self.move(self.left, self.top)
        if self.top < 0:
            self.top = 0
            self.move(self.left, 0)


class Start(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/startup.ui", self)
        self.setWindowIcon(QIcon("icon/icon.png"))

        self.button = self.findChild(QPushButton, "browse")
        self.button.clicked.connect(self.on_click)
        self.files, self.main_window = None, None

    def on_click(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Choose Image File", "",
                                                "Image Files (*.jpg *.png *.jpeg);;All Files (*)")
        if files:
            self.files = files
            self.close()
            self.main_window = Main(self.files)
            self.main_window.show()


class Main(QWidget):
    def __init__(self, files):
        # initialize
        super().__init__()
        uic.loadUi("ui\\main.ui", self)
        self.setWindowIcon(QIcon("icon/icon.png"))
        self.move(120, 100)
        self.img_list, self.rb = [], None
        for f in files:
            self.img_list.append(Images(f))
        self.img_id = 0
        self.img_class = self.img_list[self.img_id]
        self.img = QPixmap(qimage2ndarray.array2qimage(cv2.cvtColor(self.img_class.img, cv2.COLOR_BGR2RGB)))

        # find widgets and connect them
        self.vbox = self.findChild(QVBoxLayout, "vbox")
        self.base_frame = self.findChild(QFrame, "base_frame")
        self.filter_btn = self.findChild(QPushButton, "filter_btn")
        self.filter_btn.clicked.connect(self.filter_frame)
        self.adjust_btn = self.findChild(QPushButton, "adjust_btn")
        self.adjust_btn.clicked.connect(self.adjust_frame)

        # display img
        self.gv = self.findChild(QGraphicsView, "gv")
        self.scene = QGraphicsScene()
        self.scene_img = self.scene.addPixmap(self.img)
        self.gv.setScene(self.scene)

        # zoom in
        self.zoom_moment = False
        self._zoom = 0

        # rotate
        self.rotate_value = 0

    def update_img(self, movable=False):
        self.img = QPixmap(qimage2ndarray.array2qimage(cv2.cvtColor(self.img_class.img, cv2.COLOR_BGR2RGB)))
        self.scene.removeItem(self.scene_img)
        self.scene_img = self.scene.addPixmap(self.img)
        if movable:
            self.scene_img.setFlag(QGraphicsItem.ItemIsMovable)
        else:
            self.fitInView()

    def filter_frame(self):
        def click_contrast():
            self.img_class.auto_contrast()
            self.update_img()
            filter_frame.contrast_btn.clicked.disconnect(click_contrast)

        def click_sharpen():
            self.img_class.auto_sharpen()
            self.update_img()
            filter_frame.sharpen_btn.clicked.disconnect(click_sharpen)

        def click_cartoon():
            self.img_class.auto_cartoon()
            self.update_img()
            filter_frame.cartoon_btn.clicked.disconnect(click_cartoon)

        def click_cartoon1():
            self.img_class.auto_cartoon(1)
            self.update_img()
            filter_frame.cartoon_btn1.clicked.disconnect(click_cartoon1)

        def click_invert():
            self.img_class.auto_invert()
            self.update_img()
            filter_frame.invert_btn.clicked.disconnect(click_invert)

        def click_y():
            filter_frame.frame.setParent(None)
            self.img_class.img_copy = deepcopy(self.img_class.img)
            self.vbox.addWidget(self.base_frame)

        def click_n():
            if not np.array_equal(self.img_class.img_copy, self.img_class.img):
                msg = QMessageBox.question(self, "Cancel edits", "Confirm to discard all the changes?   ",
                                           QMessageBox.Yes | QMessageBox.No)
                if msg != QMessageBox.Yes:
                    return False

            filter_frame.frame.setParent(None)
            self.img_class.reset()
            self.update_img()
            self.vbox.addWidget(self.base_frame)

        filter_frame = Filter()
        filter_frame.y_btn.clicked.connect(click_y)
        filter_frame.n_btn.clicked.connect(click_n)
        filter_frame.contrast_btn.clicked.connect(click_contrast)
        filter_frame.sharpen_btn.clicked.connect(click_sharpen)
        filter_frame.cartoon_btn.clicked.connect(click_cartoon)
        filter_frame.cartoon_btn1.clicked.connect(click_cartoon1)
        filter_frame.invert_btn.clicked.connect(click_invert)

        self.base_frame.setParent(None)
        self.vbox.addWidget(filter_frame.frame)

    def adjust_frame(self):
        def click_crop(rotate=False):
            def click_y1():
                self.img_class.rotate_img(self.rotate_value, crop=True)
                self.img_class.crop_img(self.rb.top * 2, self.rb.bottom * 2, self.rb.left * 2, self.rb.right * 2)
                # self.img_class.change_b_c(beta=40)
                self.update_img()
                self.zoom_moment = False

                crop_frame.frame.setParent(None)
                self.vbox.addWidget(adjust_frame.frame)
                self.rb.close()

            def click_n1():
                if not np.array_equal(self.img_class.img_copy, self.img_class.img):
                    msg = QMessageBox.question(self, "Cancel edits", "Confirm to discard all the changes?   ",
                                               QMessageBox.Yes | QMessageBox.No)
                    if msg != QMessageBox.Yes:
                        return False
                self.img_class.change_b_c(beta=40)
                self.img_class.reset()
                self.update_img()
                self.zoom_moment = False

                crop_frame.frame.setParent(None)
                self.vbox.addWidget(adjust_frame.frame)
                self.rb.close()

            def change_slide():
                self.rotate_value = crop_frame.slider.value()
                self.img_class.rotate_img(self.rotate_value)

                self.rb.setGeometry(self.img_class.left, self.img_class.top, self.img_class.right - self.img_class.left,
                                    self.img_class.bottom - self.img_class.top)
                self.rb.update_dim()
                self.update_img(True)

            crop_frame = Crop()
            crop_frame.n_btn.clicked.connect(click_n1)
            crop_frame.y_btn.clicked.connect(click_y1)
            crop_frame.slider.valueChanged.connect(change_slide)
            adjust_frame.frame.setParent(None)
            self.vbox.addWidget(crop_frame.frame)

            self.rb = ResizableRubberBand(self.gv, self.img_class, self.update_img)
            self.rb.setGeometry(300, 200, 400, 250)
            self.img_class.change_b_c(beta=-40)
            if not rotate:
                crop_frame.slider.setParent(None)
                self.update_img()
            else:
                self.zoom_moment = True
                self.update_img(True)

        def click_y():
            self.start_detect = False
            adjust_frame.frame.setParent(None)
            self.img_class.img_copy = deepcopy(self.img_class.img)
            self.vbox.addWidget(self.base_frame)

        def click_n():
            if not np.array_equal(self.img_class.img_copy, self.img_class.img):
                msg = QMessageBox.question(self, "Cancel edits", "Confirm to discard all the changes?   ",
                                           QMessageBox.Yes | QMessageBox.No)
                if msg != QMessageBox.Yes:
                    return False

            self.start_detect = False
            adjust_frame.frame.setParent(None)
            self.img_class.reset()
            self.update_img()
            self.vbox.addWidget(self.base_frame)

        adjust_frame = Adjust()
        adjust_frame.y_btn.clicked.connect(click_y)
        adjust_frame.n_btn.clicked.connect(click_n)
        adjust_frame.crop_btn.clicked.connect(click_crop)
        adjust_frame.rotate_btn.clicked.connect(lambda _: click_crop(rotate=True))

        self.base_frame.setParent(None)
        self.vbox.addWidget(adjust_frame.frame)

    def wheelEvent(self, event):
        if self.zoom_moment:
            if event.angleDelta().y() > 0:
                factor = 1.25
                self._zoom += 1
            else:
                factor = 0.8
                self._zoom -= 1
            if self._zoom > 0:
                self.gv.scale(factor, factor)
            elif self._zoom == 0:
                self.fitInView()
            else:
                self._zoom = 0

    def fitInView(self):
        rect = QRectF(self.img.rect())
        if not rect.isNull():
            self.gv.setSceneRect(rect)

            unity = self.gv.transform().mapRect(QRectF(0, 0, 1, 1))
            self.gv.scale(1 / unity.width(), 1 / unity.height())
            view_rect = self.gv.viewport().rect()
            scene_rect = self.gv.transform().mapRect(rect)
            factor = min(view_rect.width() / scene_rect.width(),
                         view_rect.height() / scene_rect.height())
            self.gv.scale(factor, factor)
            self._zoom = 0


def main():
    app = QApplication(sys.argv)
    window = Start()
    window.show()
    app.exec_()


if __name__ == "__main__":
    main()