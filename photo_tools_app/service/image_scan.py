# _*_ coding: utf-8 _*_

import cv2
import numpy as np
from scipy.ndimage import gaussian_filter
from imutils import perspective
from skimage.filters import threshold_local


class ScanImage:

    @staticmethod
    def gauss_division(image):
        src1 = image.astype(np.float32)
        # gauss = ScanImage.gaussian_filter(image, sigma=200)
        gauss = cv2.GaussianBlur(image, (5, 5), 0)
        gauss1 = gauss.astype(np.float32)
        dst1 = (src1 / gauss1) * 255
        return dst1

    @staticmethod
    def cv2_enhance_contrast(img, factor=2.1):
        # tmp = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        mean = cv2.mean(img)[0]
        mean = np.uint8(mean)
        img_deg = np.ones_like(img) * mean
        return cv2.addWeighted(img, factor, img_deg, 1 - factor, 0.0)

    @staticmethod
    def get_scan_img(img):
        tmp = ScanImage.gauss_division(img)
        return ScanImage.cv2_enhance_contrast(tmp, 5)

    @staticmethod
    def rectify(h):
        h = h.reshape((4, 2))  # 改变数组的形状，变成4*2形状的数组
        hnew = np.zeros((4, 2), dtype=np.float32)  # 创建一个4*2的零矩阵
        # 确定检测文档的四个顶点
        add = h.sum(1)
        hnew[0] = h[np.argmin(add)]  # argmin()函数是返回最大数的索引
        hnew[2] = h[np.argmax(add)]

        diff = np.diff(h, axis=1)  # 沿着制定轴计算第N维的离散差值
        hnew[1] = h[np.argmin(diff)]
        hnew[3] = h[np.argmax(diff)]

        return hnew


    # 判断轮廓 有轮廓就输出轮廓的内容
    @staticmethod
    def get_outline_scan_img(img_path):
        image = cv2.imread(img_path)
        orig = image.copy()
        # 灰度转化
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # 滤波
        gray_image = cv2.GaussianBlur(gray_image, (5, 5), 0)
        # 边缘检测
        canny_image = cv2.Canny(gray_image, 0, 50)
        # 查找轮廓
        contours, hierarchy = cv2.findContours(canny_image.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)

        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:2]
        screenCnt = None
        for c in contours:
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.018 * peri, True)
            if len(approx) == 4:
                screenCnt = approx
                break
        if screenCnt is None:
            print("No contour detected")
        else:

            # 将目标映射到800*800四边形
            # approx = ScanImage.rectify(screenCnt)
            # pts2 = np.float32([[0, 0], [800, 0], [800, 800], [0, 800]])
            #
            # # 透视变换
            # # 使用gtePerspectiveTransform函数获得透视变换矩阵：approx是源图像中四边形的4个定点集合位置；pts2是目标图像的4个定点集合位置
            # M = cv2.getPerspectiveTransform(approx, pts2)
            #
            # # 使用warpPerspective函数对源图像进行透视变换，输出图像dst大小为800*800
            # dst = cv2.warpPerspective(orig, M, (800, 800))
            # # 画出轮廓，-1表示所有的轮廓，画笔颜色为（0,255,0），粗细为2
            # cv2.drawContours(image, [screenCnt], -1, (0, 255, 0), 2)
            # # 对透视变换后的图像进行灰度处理
            # dst = cv2.cvtColor(dst, cv2.COLOR_BGR2GRAY)

            # 第二个参数为领域内像素点加权和，权重为一个高斯窗口，第五个参数为规定正方形领域大小（11*11），第六个参数是常数C：阈值等于加权值减去这个常数
            # th4 = cv2.adaptiveThreshold(dst, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)


            # # 视角
            warped = perspective.four_point_transform(orig, screenCnt.reshape(4, 2))
            # 灰度转换
            warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
            # 阈值分割
            T = threshold_local(warped, 11, offset=10, method='gaussian')
            dst = (warped > T).astype('uint8') * 255
            # scan_img = ScanImage.get_scan_img(warped)

        dst = ScanImage.cv2_enhance_contrast(dst)
        cv2.imwrite("test5.png", dst)


if __name__ == "__main__":
    img_path = r"/Users/vega/workspace/codes/py_space/working/photo-tools-api/photo_tools_app/service/rrrr.png"
    ScanImage.get_outline_scan_img(img_path)
    # image = cv2.imread(img_path)
    # scan_img = ScanImage.get_scan_img(image)
    # scan_img = ScanImage.gauss_division(image)
    # cv2.imwrite("test5.png", scan_img)