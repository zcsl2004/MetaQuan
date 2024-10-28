import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QSpinBox, QFileDialog
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QColorDialog
import random




class ImageProcessingApp(QWidget):
    def __init__(self):
        super().__init__()

        self.image_path = None
        self.image = None
        self.resized_image = None
        self.gray_image = None
        self.binary_image = None
        self.output_image = None
        self.contours = None
        self.combined_image = None
        self.resized_image_2 = None
        self.new_grid_image = None
        self.result_image = None
        self.second_phase_volume_grid = 0
        self.estimated_grain_size = 0
        self.second_phase_percentage_area = 0
        self.current_choice = 'up'
        self.show_intercept_line = False
        self.grid_color=(0,255,255)

        self.initUI()

    def initUI(self):

        #设置名称
        self.setWindowTitle("金相定量")
        # 创建加载图片按钮
        self.load_button = QPushButton('加载图片')
        self.load_button.clicked.connect(self.loadImage)

        # 创建保存图片按钮
        self.save_button = QPushButton('保存图片')
        self.save_button.clicked.connect(self.saveImage)

        # 创建二值化阈值滑块和数值框
        self.threshold_slider = QSlider(Qt.Horizontal)
        self.threshold_slider.setMinimum(0)
        self.threshold_slider.setMaximum(255)
        self.threshold_slider.setValue(128)
        self.threshold_slider.valueChanged.connect(self.updateSpinboxFromSlider)
        self.threshold_spinbox = QSpinBox()
        self.threshold_spinbox.setMinimum(0)
        self.threshold_spinbox.setMaximum(255)
        self.threshold_spinbox.setValue(128)
        self.threshold_spinbox.valueChanged.connect(self.updateBinaryImageFromSpinbox)

        # 创建选择按钮
        self.choice_button = QPushButton('切换')
        self.choice_button.clicked.connect(self.toggleChoice)

        # 创建截点法按钮、网格长度滑块和数值框、放大倍数滑块和数值框
        self.intercept_button = QPushButton('截点法')
        self.intercept_button.clicked.connect(self.updateCombinedImage)
        self.grid_length_slider_intercept = QSlider(Qt.Horizontal)
        self.grid_length_slider_intercept.setMinimum(1)
        self.grid_length_slider_intercept.setMaximum(50)
        self.grid_length_slider_intercept.setValue(15)
        self.grid_length_slider_intercept.valueChanged.connect(self.updateCombinedImagelengthSlider)
        self.grid_length_spinbox_intercept = QSpinBox()
        self.grid_length_spinbox_intercept.setMinimum(1)
        self.grid_length_spinbox_intercept.setMaximum(50)
        self.grid_length_spinbox_intercept.setValue(15)
        self.grid_length_spinbox_intercept.valueChanged.connect(self.updateCombinedImagelengthSpinbox)
        self.magnification_slider = QSlider(Qt.Horizontal)
        self.magnification_slider.setMinimum(0)
        self.magnification_slider.setMaximum(50)
        self.magnification_slider.setValue(15)
        self.magnification_slider.valueChanged.connect(self.updateCombinedImagemagnSlider)
        self.magnification_spinbox = QSpinBox()
        self.magnification_spinbox.setMinimum(0)
        self.magnification_spinbox.setMaximum(50)
        self.magnification_spinbox.setValue(15)
        self.magnification_spinbox.valueChanged.connect(self. updateCombinedImagemagnSpinbox)

        # 创建网格法按钮、新网格长度滑块和数值框、网格颜色选择按钮
        self.grid_method_button = QPushButton('网格法')
        self.grid_method_button.clicked.connect(self.updategridcalculatevolume)
        self.new_grid_length_slider = QSlider(Qt.Horizontal)
        self.new_grid_length_slider.setMinimum(0)
        self.new_grid_length_slider.setMaximum(200)
        self.new_grid_length_slider.setValue(80)
        self.new_grid_length_slider.valueChanged.connect(self.updategridcalculatevolumeFromslider)
        self.new_grid_length_spinbox = QSpinBox()
        self.new_grid_length_spinbox.setMinimum(0)
        self.new_grid_length_spinbox.setMaximum(200)
        self.new_grid_length_spinbox.setValue(80)
        self.new_grid_length_spinbox.valueChanged.connect(self.updategridcalculatevolumeFromSpinbox)
        self.grid_color_button = QPushButton('选择网格颜色')
        self.grid_color_button.clicked.connect(self.selectGridColor)

        # 创建面积法按钮
        self.area_method_button = QPushButton('面积法')
        self.area_method_button.clicked.connect(self.calculateAreaPercentage)

        # 创建截点数和晶粒度输出框
        self.intercept_count_label = QLabel('截点总数：')
        self.grain_size_label = QLabel('平均晶粒尺寸：')

        # 创建第二相体积（网格法）输出框
        self.second_phase_volume_label = QLabel('第二相体积（网格法）：')

        # 创建第二相百分含量（面积法）输出框
        self.second_phase_percentage_label = QLabel('第一相百分含量（面积法）：')

        # 创建原图显示标签
        self.original_image_label = QLabel()

        # 创建处理后图像显示标签
        self.processed_image_label = QLabel()

        # 布局设置
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.load_button)
        top_layout.addWidget(self.save_button)

        second_layout = QHBoxLayout()
        second_layout.addWidget(QLabel('二值化阈值：'))
        second_layout.addWidget(self.threshold_slider)
        second_layout.addWidget(self.threshold_spinbox)

        third_layout = QHBoxLayout()
        third_layout.addWidget(self.choice_button)

        fourth_layout = QHBoxLayout()
        fourth_layout.addWidget(self.intercept_button)
        fourth_layout.addWidget(QLabel('截线长度：'))
        fourth_layout.addWidget(self.grid_length_slider_intercept)
        fourth_layout.addWidget(self.grid_length_spinbox_intercept)
        fourth_layout.addWidget(QLabel('截线数量：'))
        fourth_layout.addWidget(self.magnification_slider)
        fourth_layout.addWidget(self.magnification_spinbox)

        fifth_layout = QHBoxLayout()
        fifth_layout.addWidget(self.grid_method_button)
        fifth_layout.addWidget(QLabel('新网格长度：'))
        fifth_layout.addWidget(self.new_grid_length_slider)
        fifth_layout.addWidget(self.new_grid_length_spinbox)
        fifth_layout.addWidget(self.grid_color_button)

        sixth_layout = QHBoxLayout()
        sixth_layout.addWidget(self.area_method_button)

        output_layout = QHBoxLayout()
        output_layout.addWidget(self.intercept_count_label)
        output_layout.addWidget(self.grain_size_label)
        output_layout.addWidget(self.second_phase_volume_label)
        output_layout.addWidget(self.second_phase_percentage_label)

        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.original_image_label)
        bottom_layout.addWidget(self.processed_image_label)

        author_layout = QHBoxLayout()
        author_label = QLabel('作者：zcsl')
        author_layout.addWidget(author_label)

        main_layout = QVBoxLayout()
        main_layout.addLayout(top_layout)
        main_layout.addLayout(second_layout)
        main_layout.addLayout(third_layout)
        main_layout.addLayout(fourth_layout)
        main_layout.addLayout(fifth_layout)
        main_layout.addLayout(sixth_layout)
        main_layout.addLayout(output_layout)
        main_layout.addLayout(bottom_layout)
        main_layout.addLayout(author_layout)

        self.setLayout(main_layout)
#加载图片
    def loadImage(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.image_path, _ = QFileDialog.getOpenFileName(self, "选择图像文件", "", "图像文件 (*.jpg *.png *.bmp);;所有文件 (*)",
                                                          options=options)
        if self.image_path:
            try:
                self.image = cv2.imread(self.image_path)
                if self.image is None:
                    raise ValueError("无法读取图像文件")
                self.resized_image = cv2.resize(self.image, (640, 480))
                self.gray_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
                _, self.binary_image = cv2.threshold(self.gray_image, self.threshold_slider.value(), 255,
                                                     cv2.THRESH_BINARY_INV)
                self.result_image = self.image
                self.showImage()
                self.displayImage()

            except Exception as e:
                print(f"加载图像时出现错误：{e}")
#保存图片
    def saveImage(self):
        if self.result_image is not None:
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            file_path, _ = QFileDialog.getSaveFileName(self, "保存图像", "", "图像文件 (*.jpg *.png *.bmp);;所有文件 (*)",
                                                       options=options)
            if file_path:
                try:
                    cv2.imwrite(file_path, self.result_image)
                    #self.result_image = None
                except Exception as e:
                    print(f"保存图像时出现错误：{e}")
#二值化
    def updateBinaryImage(self):
        try:
            _, self.binary_image = cv2.threshold(self.gray_image, self.threshold_slider.value(), 255, cv2.THRESH_BINARY_INV)

            self.result_image = self.binary_image
            self.showImage()
        except Exception as e:
            print(f"更新二值化图像时出现错误：{e}")

#二值化控件设置
    def updateBinaryImageFromSpinbox(self):
        self.threshold_slider.setValue(self.threshold_spinbox.value())
        self.updateBinaryImage()

    def updateSpinboxFromSlider(self):
        self.threshold_spinbox.setValue(self.threshold_slider.value())
        self.updateBinaryImageFromSpinbox()

#裁剪位置翻转
    def toggleChoice(self):
        if self.binary_image is not None and self.image is not None:
            self.output_image = 255 * np.ones_like(self.image).astype(np.uint8)
            if self.current_choice == 'up':
                for y in range(self.image.shape[0]):
                    for x in range(self.image.shape[1]):
                        if self.binary_image[y, x] == 0:
                            self.output_image[y, x] = 255
                        else:
                            self.output_image[y, x] = self.image[y, x]
            elif self.current_choice == 'down':
                for y in range(self.image.shape[0]):
                    for x in range(self.image.shape[1]):
                        if self.binary_image[y, x] == 0:
                            self.output_image[y, x] = self.image[y, x]
                        else:
                            self.output_image[y, x] = 255
            else:
                raise ValueError("无效的状态")
            # 切换状态
            self.current_choice = 'down' if self.current_choice == 'up' else 'up'
            if not self.show_intercept_line:
                self.result_image = self.output_image
                self.showImage()
        else:
            print("无法切换，图像或二值化图像为空。")

#截点法控件逻辑
    def updateCombinedImagelengthSpinbox(self):
        self.grid_length_slider_intercept.setValue(self.grid_length_spinbox_intercept.value())
        self.updateCombinedImage()

    def updateCombinedImagelengthSlider(self):
        self.grid_length_spinbox_intercept.setValue(self.grid_length_slider_intercept.value())
        self.updateCombinedImagelengthSpinbox()

    def updateCombinedImagemagnSpinbox(self):
        self.magnification_slider.setValue(self.magnification_spinbox.value())
        self.updateCombinedImage()

    def updateCombinedImagemagnSlider(self):
        self.magnification_spinbox.setValue(self.magnification_slider.value())
        self.updateCombinedImagelengthSpinbox()

#截点法
    def updateCombinedImage(self):
        self.result_image = self.image.copy()

        height, width = self.binary_image.shape

        def generate_random_line(width, height):
            x1 = random.randint(0, width - 1)
            y1 = random.randint(0, height - 1)
            x2 = random.randint(0, width - 1)
            y2 = random.randint(0, height - 1)

            return (x1, y1), (x2, y2)

        def count_intersection_points(line, img):
            x1, y1 = line[0]
            x2, y2 = line[1]
            dx = abs(x2 - x1)
            dy = abs(y2 - y1)
            sx = -1 if x1 > x2 else 1
            sy = -1 if y1 > y2 else 1
            err = dx - dy

            intersections = []
            while True:
                if 0 <= y1 < img.shape[0] and 0 <= x1 < img.shape[1] and img[y1, x1] == 255 and (
                        (0 <= y1 + sy < img.shape[0] and img[y1 + sy, x1] == 0 and sy != 0) or (
                        0 <= x1 + sx < img.shape[1] and img[y1, x1 + sx] == 0 and sx != 0)):
                    intersections.append((x1, y1))
                if x1 == x2 and y1 == y2:
                    break
                e2 = 2 * err
                if e2 > -dy:
                    err -= dy
                    x1 += sx
                if e2 < dx:
                    err += dx
                    y1 += sy
            return intersections

        def calculate_grain_diameter(line, intersection_count):
            x1, y1 = line[0]
            x2, y2 = line[1]
            length = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
            if intersection_count > 0:
                return length / intersection_count
            else:
                return 0


        lines = []
        intersection_counts = []
        grain_diameters = []
        total_intersections = 0
        result_image = self.image.copy()

        while len(lines) < self.magnification_slider.value() or total_intersections < 50:
            line = generate_random_line(width, height)
            intersections = count_intersection_points(line, self.binary_image)
            total_intersections += len(intersections)
            intersection_counts.append(len(intersections))
            grain_diameter = calculate_grain_diameter(line, len(intersections))
            grain_diameters.append(grain_diameter)
            lines.append(line)
            if total_intersections > 60:
                # 减少截线长度
                for i in range(len(lines)):
                    p1, p2 = lines[i]
                    x1, y1 = p1
                    x2, y2 = p2
                    new_x1 = x1 + random.randint(-width // 4, width // 4)
                    new_y1 = y1 + random.randint(-height // 4, height // 4)
                    new_x2 = x2 + random.randint(-width // 4, width // 4)
                    new_y2 = y2 + random.randint(-height // 4, height // 4)
                    new_length = np.sqrt((new_x2 - new_x1) ** 2 + (new_y2 - new_y1) ** 2)
                    if new_length < self.grid_length_slider_intercept.value():
                        lines[i] = (new_x1, new_y1), (new_x2, new_y2)


        # 绘制截线和截点
        result_img =  self.image.copy()
        for line in lines:
            cv2.line(result_img, line[0], line[1], (0, 0, 255), 2)
            intersections = count_intersection_points(line, self.binary_image)
            for point in intersections:
                cv2.circle(result_img, point, 15, (0, 0, 0), -1)

        # 计算平均晶粒尺寸
        average_grain_size = sum(grain_diameters) / len(grain_diameters)



        self.estimated_grain_size = average_grain_size
        self.result_image = result_img
        self.showImage()
        self.intercept_count_label.setText(f'截点数：{total_intersections}')
        self.grain_size_label.setText(f'平均晶粒尺寸：{self.estimated_grain_size}')


#网格法
    def updategridcalculatevolume(self):
        if self.binary_image is not None:
            # 读取图像
            binary_image = self.binary_image

            # 获取滑块值
            slider_value = self.new_grid_length_slider.value()
            # 建立反向关系，确保滑块值增大时网格长度减小
            new_grid_length = self.new_grid_length_slider.value()

            # 二、计算第二相体积（网格法）
            resized_image_2 = self.image.copy()
            new_grid_image = np.zeros_like(resized_image_2)
            for y in range(0, resized_image_2.shape[0], new_grid_length):
                cv2.line(resized_image_2, (0, y), (resized_image_2.shape[1], y), (0, 255, 0), 1)
                for x in range(0, resized_image_2.shape[1], new_grid_length):
                    cv2.line(resized_image_2, (x, 0), (x, resized_image_2.shape[0]), (0, 255, 0), 1)

            total_new_grid_points = ((resized_image_2.shape[0] // new_grid_length) + 1) * (
                    (resized_image_2.shape[1] // new_grid_length) + 1)
            points_on_second_phase = 0
            for y in range(0, resized_image_2.shape[0], new_grid_length):
                for x in range(0, resized_image_2.shape[1], new_grid_length):
                    grid_section = binary_image[y:y + new_grid_length, x:x + new_grid_length]
                    count = np.sum(grid_section == 0)
                    if count > new_grid_length * new_grid_length / 2:
                        points_on_second_phase += 1
            second_phase_volume_grid = points_on_second_phase / total_new_grid_points

            # 在原图上绘制网格
            grid_image = self.image.copy()
            for y in range(0, self.image.shape[0], new_grid_length):
                cv2.line(grid_image, (0, y), (self.image.shape[1], y), self.grid_color, 1)
                for x in range(0, self.image.shape[1], new_grid_length):
                    cv2.line(grid_image, (x, 0), (x, self.image.shape[0]), self.grid_color, 1)

            self.result_image = grid_image
            self.showImage()
            self.second_phase_volume_label.setText(f'第二相体积（网格法）：{second_phase_volume_grid}')

        else:
            print("无法更新调整后的图像，图像或二值化图像为空。")

#网格法控件设置
    def updategridcalculatevolumeFromSpinbox(self):
        self.new_grid_length_slider.setValue(self.new_grid_length_spinbox.value())
        self.updategridcalculatevolume()

    def updategridcalculatevolumeFromslider(self):
        self.new_grid_length_spinbox.setValue(self.new_grid_length_slider.value())
        self.updategridcalculatevolumeFromSpinbox()

    def selectGridColor(self):
        try:
            color = QColorDialog.getColor()
            if color.isValid():
                self.grid_color = (color.red(), color.green(), color.blue())
            self.updategridcalculatevolume()
        except Exception as e:
            print(f"选择网格颜色时出现错误：{e}")

#面积法
    def calculateAreaPercentage(self):
        if self.binary_image is not None:
            print(f"二值化图像形状：{self.binary_image.shape}")
            black_pixels = np.sum(self.binary_image == 0)
            total_pixels = self.binary_image.shape[0] * self.binary_image.shape[1]
            ratio = black_pixels / total_pixels
            self.second_phase_percentage_label.setText(f'第二相百分含量（面积法））：{ratio * 100}%')
        else:
            print("无法计算面积百分比，图像或二值化图像为空。")
            print(f"当前 binary_img 的值为：{self.self.binary_image}")

#显示结果图
    def showImage(self):
        if self.result_image is not None:
            self.resized_image = cv2.resize(self.result_image,(640,480))
            qimage = self.convertCVImageToQImage(self.resized_image)

            self.processed_image_label.setPixmap(QPixmap.fromImage(qimage))
        else:
            print("无法显示图像，图像为空。")

#显示原图
    def displayImage(self):
        if self.resized_image is not None:
            qimage = self.convertCVImageToQImage(self.resized_image)

            self.original_image_label.setPixmap(QPixmap.fromImage(qimage))
        else:
            print("无法显示图像，图像为空。")


#Mat转qt
    def convertCVImageToQImage(self, cv_image):
        if len(cv_image.shape) == 2:
            height, width = cv_image.shape
            bytesPerLine = width
            return QImage(cv_image.data, width, height, bytesPerLine, QImage.Format_Grayscale8)
        else:
            height, width, channels = cv_image.shape
            bytesPerLine = channels * width
            return QImage(cv_image.data, width, height, bytesPerLine, QImage.Format_BGR888)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ImageProcessingApp()
    ex.show()
    sys.exit(app.exec_())