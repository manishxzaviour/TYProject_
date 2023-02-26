from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Canvas, Rectangle, Color
from kivy.graphics.texture import Texture
from kivy.metrics import dp
from kivy.properties import ObjectProperty, Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.widget import Widget
import os, sys
from kivy.resources import resource_add_path, resource_find

import cv2 as cv
import requests
import numpy as np
import math
import time
import json


class ImageW(Widget):
    url1 = ''
    url2 = ''
    threshP = 40
    threshC = 100
    probF = [0, 0]
    faultL1 = []
    faultL2 = []
    pos1 = [0, 0]
    pos2 = [0, 0]
    avp = [0, 0]
    iheight = 0
    dilateBlb=np.ones([5, 5], np.uint8)
    avgK=np.ones([5, 5])
    distance=[0,0]
    def __init__(self, **kwargs):
        super(ImageW, self).__init__(**kwargs)
        self.image1 = Image(pos=self.pos, size=(self.width / 2 - 10, self.height - 10))
        self.image2 = Image(pos=(self.width / 2, self.y), size=(self.width / 2 - 10, self.height - 10))
        self.add_widget(self.image1)
        self.add_widget(self.image2)
        self.l1 = Label(text="[b]Front_View_S1[/b]",font_size=22,markup=True,color="#023942",outline_color="#fcfcfc",outline_width=2)
        self.l2 = Label(text="[b]Back_View_S2[/b]",font_size=22,markup=True,color="#023942",outline_color="#fcfcfc",outline_width=2)
        self.add_widget(self.l1)
        self.add_widget(self.l2)

    def on_size(self, *args):
        self.url1 = self.parent.parent.url1
        self.url2 = self.parent.parent.url2
        self.threshP = self.parent.parent.threshP
        self.iheight = self.parent.parent.iheight
        self.dilateBlb = self.parent.parent.iheight
        self.avgK = self.parent.parent.avgK
        self.l1.pos = (self.width / 4 - 50, self.y)
        self.l2.pos = (self.width * 3 / 4 - 50, self.y)
        self.image1.pos = (self.x, self.y)
        self.image1.size = (self.width / 2 - 10, self.height - 10)
        self.image2.pos = (self.width / 2, self.y)
        self.image2.size = (self.width / 2, self.height - 10)

    def update1(self, dt):
        self.url1 = self.parent.parent.url1
        self.url2 = self.parent.parent.url2
        self.threshP = self.parent.parent.threshP
        self.iheight = self.parent.parent.iheight
        self.dilateBlb=self.parent.parent.dilateBlb
        self.avgK=self.parent.parent.avgK
        st = time.time()
        img = requests.get(self.url1 + 'capture?', stream=True).raw
        image = np.asarray(bytearray(img.read()), dtype='uint8')
        image = cv.imdecode(image, cv.IMREAD_COLOR)
        image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
        image = image[0:self.iheight, :]
        image = cv.filter2D(image, -1, self.avgK/(self.avgK.shape[0]*self.avgK.shape[1]))
        imageEnh = cv.adaptiveThreshold(image, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 11, 2)
        canny_output = cv.Canny(imageEnh, 80, 150, )
        cannyBlb = cv.dilate(canny_output, self.dilateBlb);
        cdstP = cv.cvtColor(cannyBlb, cv.COLOR_GRAY2BGR)
        linesP = cv.HoughLinesP(cannyBlb, 1, np.pi / 180, 50, None, 50, 10)
        if linesP is not None:
            for i in range(0, len(linesP)):
                l = linesP[i][0]
                self.pos1[0] += l[1]
                self.pos2[0] += l[3]
        try:
            self.pos1[0] = math.floor(self.pos1[0] / (len(linesP) + 1))
            self.pos2[0] = math.floor(self.pos2[0] / (len(linesP) + 1))
            self.avp[0] = self.pos1[0] + self.pos2[0]
            self.avp[0] /= 2
        except TypeError:
            print('error: TypeError')
            self.pos1[0] = 0
            self.pos1[0] = 0
            self.avp[0] = 0
        cv.line(cdstP, (0, self.pos1[0]), (canny_output.shape[1], self.pos2[0]), (255, 150, 120), 1, cv.LINE_AA)
        for x in range(0, canny_output.shape[0]):
            for y in range(0, canny_output.shape[1]):
                if canny_output[x][y] == 255 and abs(x - self.avp[0]) > self.threshP:
                    cdstP[x][y] = [0, 0, 255]
                    self.faultL1.append([x, y]);
                    self.probF[0] += 1
        cv.imshow('img', image)
        buffer = cdstP.tostring()
        texture = Texture.create(size=(cdstP.shape[1], cdstP.shape[0]), colorfmt='bgr')
        texture.blit_buffer(buffer, colorfmt='bgr', bufferfmt='ubyte')
        self.image1.texture = texture
        en = time.time()
        x = open('frameLog1.txt', 'a')
        x.write(str(int((en - st) * 1000)) + '\n')
        x.close()
        print(f'frame1 :{int((en - st) * 1000)}')
        if (self.probF[0] > self.threshC):
            x = open('log1.txt', 'a')
            # x.write('!! mechanical failure detected !!')
            # x.write('\n')
            x.write(f'fault detected at [location] {self.distance[0]} (m) from initial position')
            # x.write('\n')
            # x.write(str(self.faultL1))
            x.write('\n')
            x.close()
            self.parent.parent.logC[0]+=1

    def update2(self, dt):
        self.url1 = self.parent.parent.url1
        self.url2 = self.parent.parent.url2
        self.threshP = self.parent.parent.threshP
        self.iheight = self.parent.parent.iheight
        self.dilateBlb = self.parent.parent.dilateBlb
        self.avgK = self.parent.parent.avgK
        st = time.time()
        img = requests.get(self.url2 + 'capture?', stream=True).raw
        image = np.asarray(bytearray(img.read()), dtype='uint8')
        image = cv.imdecode(image, cv.IMREAD_COLOR)
        image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
        # image = image[0:image.shape[0], :]
        image = image[0:self.iheight, :]
        image = cv.filter2D(image, -1, self.avgK / (self.avgK.shape[0] * self.avgK.shape[1]))
        imageEnh = cv.adaptiveThreshold(image, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 11, 2)
        canny_output = cv.Canny(imageEnh, 80, 150, )
        cannyBlb = cv.dilate(canny_output, self.dilateBlb);
        cdstP = cv.cvtColor(cannyBlb, cv.COLOR_GRAY2BGR)
        cv.imshow('img2',image)
        linesP = cv.HoughLinesP(cannyBlb, 1, np.pi / 180, 50, None, 50, 10)
        if linesP is not None:
            for i in range(0, len(linesP)):
                l = linesP[i][0]
                self.pos1[1] += l[1]
                self.pos2[1] += l[3]
        try:
            self.pos1[1] = math.floor(self.pos1[1] / (len(linesP) + 1))
            self.pos2[1] = math.floor(self.pos2[1] / (len(linesP) + 1))
            self.avp[1] = self.pos1[1] + self.pos2[1]
            self.avp[1] /= 2
        except TypeError:
            print('error: TypeError')
            self.pos1[1] = 0
            self.pos1[1] = 0
            self.avp[1] = 0
        cv.line(cdstP, (0, self.pos1[1]), (canny_output.shape[1], self.pos2[1]), (255, 150, 120), 1, cv.LINE_AA)
        for x in range(0, canny_output.shape[0]):
            for y in range(0, canny_output.shape[1]):
                if canny_output[x][y] == 255 and abs(x - self.avp[1]) > self.threshP:
                    cdstP[x][y] = [0, 0, 255]
                    self.faultL2.append([x, y]);
                    self.probF[1] += 1
        # cv.imshow('img', cdstP)
        buffer = cdstP.tostring()
        texture = Texture.create(size=(cdstP.shape[1], cdstP.shape[0]), colorfmt='bgr')
        texture.blit_buffer(buffer, colorfmt='bgr', bufferfmt='ubyte')
        self.image2.texture = texture
        # cv.imwrite('img.png',cdstP)
        en = time.time()
        x = open('frameLog2.txt', 'a')
        x.write(str(int((en - st) * 1000)) + '\n')
        x.close()
        print(f'frame2 :{int((en - st) * 1000)}')
        if (self.probF[1] > self.threshC):
            x = open('log2.txt', 'a')
            # x.write('!! mechanical failure detected !!')
            # x.write('\n')
            x.write(f'fault detected at [location] {self.distance[1]} (m) from initial position')
            # x.write('\n')
            # x.write(str(self.faultL2))
            # x.write()
            x.write('\n')
            x.close()
            self.parent.parent.logC[1]+=1



class Page1(Screen):
    time = 0
    jsonD = {}
    iheight = 0
    threshP = 0
    logC=[0,0]
    dilateBlb = np.ones([5, 5], np.uint8)
    avgK = np.ones([5, 5])
    def __init__(self, **kwargs):
        jsonF = open('config.json', 'r')
        jsonD = json.load(jsonF)
        self.jsonD = jsonD
        self.url1 = jsonD["url1"]
        self.url2 = jsonD["url2"]
        self.iheight = jsonD["iheight"]
        self.threshP = jsonD["thresh"]
        self.flag1 = 1
        self.flag2 = 1
        super(Page1, self).__init__(**kwargs)
        pass

    def start(self):
        jsonF = open('config.json', 'r')
        jsonD = json.load(jsonF)
        self.url1 = jsonD["url1"]
        self.url2 = jsonD["url2"]
        self.iheight = jsonD["iheight"]
        self.threshP = jsonD["thresh"]
        self.dilateBlb=np.ones([jsonD["dilateBlb"],jsonD["dilateBlb"]], np.uint8)
        self.avgK=np.ones([jsonD["avgK"], jsonD["avgK"]])
        self.jsonD = jsonD
        try:
            r1 = requests.get(self.url1, timeout=2)
            self.flag1 = 1
        except requests.exceptions.ConnectionError:
            self.ids.imageScene.image1.source = 'warning.png'
            print(f"!!error: Connection Timeout [cam1] url : {self.url1}!!")
            self.flag1 = 0
        try:
            r2 = requests.get(self.url2, timeout=2)
            self.flag2 = 1
        except requests.exceptions.ConnectionError:
            self.ids.imageScene.image2.source = 'warning.png'
            print(f"!!error: Connection Timeout [cam2] url : {self.url2}!!")
            self.flag2 = 0
        if (self.flag1):
            requests.get(self.url1 + "control?", params={'var': "framesize", "val": self.jsonD["resolution"]})
            requests.get(self.url1 + "control?", params={'var': "quality", "val": self.jsonD["quality"]})
            requests.get(self.url1 + "control?", params={'var': "special_effect", "val": 0})
            requests.get(self.url1 + "control?", params={'var': "brightness", "val": self.jsonD["brightness"]})
            requests.get(self.url1 + "control?", params={'var': "contrast", "val": self.jsonD["contrast"]})
            requests.get(self.url1 + "control?", params={'var': "saturation", "val": self.jsonD["saturation"]})
            requests.get(self.url1 + "control?", params={'var': "aec", "val": self.jsonD["aecS"]})
            requests.get(self.url1 + "control?", params={'var': "aec2", "val": self.jsonD["aecDip"]})
            requests.get(self.url1 + "control?", params={'var': "gainceiling", "val": self.jsonD["gain"]})
            requests.get(self.url1 + "control?", params={'var': "hmirror", "val": self.jsonD["hflp1"]})
            requests.get(self.url1 + "control?", params={'var': "vflip", "val": self.jsonD["vflp1"]})
            Clock.schedule_interval(self.ids.imageScene.update1, self.jsonD["resolution"] / 8 + 0.01)
            requests.get(self.url1 + "control?", params={'var': "special_effect", "val": self.jsonD["filter"]})

        if (self.flag2):
            requests.get(self.url2, params={'var': "framesize", "val": self.jsonD["resolution"]})
            requests.get(self.url2 + "control?", params={'var': "framesize", "val": self.jsonD["resolution"]})
            requests.get(self.url2 + "control?", params={'var': "quality", "val": self.jsonD["quality"]})
            requests.get(self.url2 + "control?", params={'var': "special_effect", "val": 0})
            requests.get(self.url2 + "control?", params={'var': "brightness", "val": self.jsonD["brightness"]})
            requests.get(self.url2 + "control?", params={'var': "contrast", "val": self.jsonD["contrast"]})
            requests.get(self.url2 + "control?", params={'var': "saturation", "val": self.jsonD["saturation"]})
            requests.get(self.url2 + "control?", params={'var': "aec", "val": self.jsonD["aecS"]})
            requests.get(self.url2 + "control?", params={'var': "aec2", "val": self.jsonD["aecDip"]})
            requests.get(self.url2 + "control?", params={'var': "gainceiling", "val": self.jsonD["gain"]})
            requests.get(self.url2 + "control?", params={'var': "hmirror", "val": self.jsonD["hflp2"]})
            requests.get(self.url2 + "control?", params={'var': "vmirror", "val": self.jsonD["vflp2"]})
            requests.get(self.url2 + "control?", params={'var': "special_effect", "val": self.jsonD["filter"]})
            Clock.schedule_interval(self.ids.imageScene.update2, self.jsonD["resolution"] / 8 + 0.01)
        Clock.schedule_interval(self.on_time_upd, 1)

    def stop(self):
        Clock.unschedule(self.ids.imageScene.update1)
        Clock.unschedule(self.ids.imageScene.update2)
        Clock.unschedule(self.on_time_upd)
        self.ids.tog.state = 'normal'
        pass

    def toggle(self, state):
        if (state == 'normal'):
            self.stop()
        else:
            self.start()

    def on_time_upd(self, dt):
        self.ids.onT.text = str(f'On_Time(s) : {round(self.time)}')
        self.ids.logc.text=str(f'Tag_log(n): {self.logC}')
        self.time += dt


class ConfigP1(Screen):
    res = ['160x120', '240x176', '320x240', '400x296', '640x480', '800x600', '1024x768', '1280x1024', '1600x1200']
    filt = ['No effect', 'Negative', 'Grayscale', 'Red Tint', 'Green Tint', 'Blue Tint', 'Sepia', ]
    cres = 0
    cfilt = 0

    def __init__(self, **kwargs):
        super(ConfigP1, self).__init__(**kwargs)
        y = open('config.json', 'r')
        jsonD = json.load(y)
        self.ids.url1.text = jsonD["url1"]
        self.ids.url2.text = jsonD["url2"]
        self.ids.resolution.text = self.res[jsonD["resolution"]]
        self.cres=jsonD["resolution"]
        self.ids.quality.value = jsonD["quality"]
        self.ids.iheight.value = jsonD["iheight"]
        self.ids.thresh.value = jsonD["thresh"]
        self.ids.filter.text = self.filt[jsonD["filter"]]
        self.ids.brightness.value = jsonD["brightness"]
        self.ids.contrast.value = jsonD["contrast"]
        self.ids.saturation.value = jsonD["saturation"]
        self.ids.gain.value = jsonD["gain"]
        self.ids.aecS.active = (jsonD["aecS"])
        self.ids.aecDip.active = (jsonD["aecDip"])
        self.ids.hflp1.active = (jsonD["hflp1"])
        self.ids.vflp1.active = (jsonD["vflp1"])
        self.ids.hflp2.active = (jsonD["hflp2"])
        self.ids.vflp2.active = (jsonD["vflp2"])
        self.ids.avgK.value=jsonD["avgK"]
        self.ids.dilateBlb.value=jsonD["dilateBlb"]

    def save(self):
        jsonD = {
            "url1": self.ids.url1.text,
            "url2": self.ids.url2.text,
            "resolution": int(self.cres),
            "quality": int(self.ids.quality.value),
            "iheight": int(self.ids.iheight.value),
            "thresh": int(self.ids.thresh.value),
            "filter": int(self.cfilt),
            "brightness": int(self.ids.brightness.value),
            "contrast": int(self.ids.contrast.value),
            "saturation": int(self.ids.saturation.value),
            "ae": int(self.ids.ae.value),
            "aecS": int(self.ids.aecS.active),
            "aecDip": int(self.ids.aecDip.active),
            "gain": int(self.ids.gain.value),
            "hflp1": int(self.ids.hflp1.active),
            "vflp1": int(self.ids.vflp1.active),
            "hflp2": int(self.ids.hflp2.active),
            "vflp2": int(self.ids.vflp2.active),
            "avgK": int(self.ids.avgK.value),
            "dilateBlb":int(self.ids.dilateBlb.value)
        }
        y = open('config.json', 'w')
        y.write(json.dumps(jsonD, indent=4))
        y.close()
        pass

    def updRes(self, v):
        if (v == 1):
            if (self.cres < 8):
                self.cres += 1
            else:
                self.cres = 0
        if (v == -1):
            if (self.cres > 0):
                self.cres += -1
            else:
                self.cres = 8
        self.ids.resolution.text = f'{self.res[self.cres]}'
        pass

    def updFilt(self, v):
        if (v == 1):
            if (self.cfilt < 6):
                self.cfilt += 1
            else:
                self.cfilt = 0
        if (v == -1):
            if (self.cfilt > 0):
                self.cfilt += -1
            else:
                self.cfilt = 6
        self.ids.filter.text = f'{self.filt[self.cfilt]}'
        pass


class laraApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(Page1(name="mainScreen"))
        sm.add_widget(ConfigP1(name="configScreen"))
        return sm


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
