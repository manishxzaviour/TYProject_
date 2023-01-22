from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Canvas, Rectangle, Color
from kivy.graphics.texture import Texture
from kivy.metrics import dp
from kivy.properties import ObjectProperty, Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.widget import Widget
import cv2 as cv
import requests
import numpy as np
import math
import time


class ImageW(Widget):
    url = 'http://192.168.0.104/capture?_cb='
    threshP = 40
    threshC = 100
    probF = 0;
    faultL = []
    pos1 = 0
    pos2 = 0
    imageWidth=300
    def __init__(self, **kwargs):
        super(ImageW, self).__init__(**kwargs)
        with self.canvas:
            Color(.2, .2, .2, 1)
            self.b1=Rectangle(pos=self.pos, size=(self.width / 2 - 10, self.height - 10))
            self.b2=Rectangle(pos=(self.width / 2, self.y), size=(self.width / 2 - 10, self.height - 10))
        self.image1 = Image(pos=self.pos, size=(self.width / 2 - 10, self.height - 10))
        self.image2 = Image(pos=(self.width / 2, self.y), size=(self.width / 2 - 10, self.height - 10))
        self.add_widget(self.image1)
        self.add_widget(self.image2)
        Clock.schedule_interval(self.update,.5)
    def on_size(self,*args):
        requests.get('http://192.168.0.104/control?var=framesize&val=10')
        self.b1.size = (self.width / 2 - 10, self.height - 10)
        self.b2.pos = (self.width / 2, self.y)
        self.b2.size = (self.width / 2, self.height - 10)
        self.image1.size=(self.width / 2 - 10, self.height - 10)
        self.image2.pos=(self.width / 2, self.y)
        self.image2.size=(self.width / 2, self.height - 10)
    def update(self,dt):
        # requests.get('http://192.168.0.104/control?var=framesize&val=8')
        st = time.time()
        img = requests.get(self.url + str(time.time()), stream=True).raw
        image = np.asarray(bytearray(img.read()), dtype='uint8')
        image = cv.imdecode(image, cv.IMREAD_COLOR)
        image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
        # image = image[0:image.shape[0], :]
        image = image[0:self.imageWidth, :]
        image = cv.filter2D(image, -1, np.ones([5, 5]) / 25)
        imageEnh = cv.adaptiveThreshold(image, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 11, 2)
        canny_output = cv.Canny(imageEnh, 80, 150, )
        cannyBlb = cv.dilate(canny_output, np.ones([5, 5], np.uint8));
        cdstP = cv.cvtColor(cannyBlb, cv.COLOR_GRAY2BGR)
        linesP = cv.HoughLinesP(cannyBlb, 1, np.pi / 180, 50, None, 50, 10)
        if linesP is not None:
            for i in range(0, len(linesP)):
                l = linesP[i][0]
                self.pos1 += l[1]
                self.pos2 += l[3]
        self.pos1 = math.floor(self.pos1 / (len(linesP) + 1))
        self.pos2 = math.floor(self.pos2 / (len(linesP) + 1))
        self.avp = self.pos1 + self.pos2
        self.avp /= 2
        cv.line(cdstP, (0, self.pos1), (canny_output.shape[1], self.pos2), (255, 150, 120), 1, cv.LINE_AA)
        for x in range(0, canny_output.shape[0]):
            for y in range(0, canny_output.shape[1]):
                if canny_output[x][y] == 255 and abs(x - self.avp) > self.threshP:
                    cdstP[x][y] = [0, 0, 255]
                    self.faultL.append([x, y]);
                    self.probF += 1
        # cv.imshow('img', cdstP)
        buffer=cdstP.tostring()
        texture=Texture.create(size=(cdstP.shape[1],cdstP.shape[0]),colorfmt='bgr')
        texture.blit_buffer(buffer,colorfmt='bgr',bufferfmt='ubyte')
        self.image1.texture=texture
        self.image2.texture=texture
        # cv.imwrite('img.png',cdstP)
        en = time.time()
        print((en - st) * 1000)
        if (self.probF > self.threshC):
            x=open('log.txt','a')
            x.write('!! mechanical failure detected !!')
            x.write('\n')
            x.write('fault detected at pixel locations:')
            x.write('\n')
            x.write(str(self.faultL))
            x.write('\n')
            x.close()


class MainWidget(Widget):
    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
    def configBp(self):
        pass


class laraApp(App):
    def build(self):
        return MainWidget()


if __name__ == '__main__':
    laraApp().run()

# url = 'http://192.168.0.104/capture?_cb='
# requests.get('http://192.168.0.104/control?var=framesize&val=8')
# threshP = 40
# threshC = 100
# probF = 0;
# faultL = []
# pos1 = 0
# pos2 = 0
# while (1):
#     st = time.time()
#     img = requests.get(self.url + str(time.time()), stream=True).raw
#     image = np.asarray(bytearray(img.read()), dtype='uint8')
#     image = cv.imdecode(image, cv.IMREAD_COLOR)
#     image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
#     image = image[0:300, :]
#     image = cv.filter2D(image, -1, np.ones([5, 5]) / 25)
#     imageEnh = cv.adaptiveThreshold(image, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 11, 2)
#     canny_output = cv.Canny(imageEnh, 80, 150, )
#     cannyBlb = cv.dilate(canny_output, np.ones([5, 5], np.uint8));
#     cdstP = cv.cvtColor(cannyBlb, cv.COLOR_GRAY2BGR)
#     linesP = cv.HoughLinesP(cannyBlb, 1, np.pi / 180, 50, None, 50, 10)
#     if linesP is not None:
#         for i in range(0, len(linesP)):
#             l = linesP[i][0]
#             self.pos1 += l[1]
#             self.pos2 += l[3]
#     self.pos1 = math.floor(self.pos1 / (len(linesP) + 1))
#     self.pos2 = math.floor(self.pos2 / (len(linesP) + 1))
#     self.avp = self.pos1 + self.pos2
#     self.avp /= 2
#     cv.line(cdstP, (0, self.pos1), (650, self.pos2), (255, 150, 120), 1, cv.LINE_AA)
#     for x in range(0, 300):
#         for y in range(0, 640):
#             if canny_output[x][y] == 255 and abs(x - self.avp) > self.threshP:
#                 cdstP[x][y] = [0, 0, 255]
#                 self.faultL.append([x, y]);
#                 self.probF += 1
#     # cv.imshow('img', cdstP)
#     # cv.imwrite('img.png',cdstP)
#     en = time.time()
#     print((en - st) * 1000)
#     # if cv.waitKey(25) & 0xFF == ord('q'):
#     #     break
#     # if (self.probF > self.threshC):
#     #     print('!! mechanical failure detected !!')
#     #     print('fault detected at pixel locations:')
#     #     print(self.faultL)
# cv.waitKey()
