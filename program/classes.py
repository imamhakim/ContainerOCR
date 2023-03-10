import threading
from threading import Thread
from roboflow import Roboflow
import cv2
import easyocr
import numpy
import mysql.connector
from ultralytics import YOLO

global model, reader, db, cursor

### Inisiasi EasyOCR
reader = easyocr.Reader(['en'],gpu=False)

### Inisiasi pembacaan container
rf = Roboflow(api_key="n0I6AKgAqsWoITl7qxNg")
project = rf.workspace().project("shipping-containers-bdotu")
model = project.version(1).model

### Inisiasi Database
# Masukkan host, user, password serta database yang digunakan ###
HOST = 'localhost'
USER = 'root'
PASSWORD = ''
DATABASE = 'dataocr'

### untuk koneksi ke database berdasarkan input diatas
db = mysql.connector.connect(
            host = HOST,
            user = USER,
            password = PASSWORD,
            database = DATABASE,
        )

if db.is_connected():
    print("Database is connected")
else:
    print("Database is disconnect")
cursor = db.cursor()

create_table1 = """
CREATE TABLE IF NOT EXISTS dataocr (
    CameraSource VARCHAR(40),
    Code1 VARCHAR(20),
    Code2 VARCHAR(20),
    timestamp TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP
);
"""
create_table2 = """
CREATE TABLE IF NOT EXISTS datatruck (
    TruckStatus VARCHAR(10),
    CameraSource VARCHAR(10),
    timestamp TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP
);
"""
cursor.execute(create_table1)
cursor.execute(create_table2)

class VideoStream:
    """
    Class for grabbing frames from CV2 video capture.

    `Attributes:`
        stream: CV2 VideoCapture object
        grabbed: bool indication whether the frame from VideoCapture() was read correctly
        frame: the frame from VideoCapture()
        stopped: bool indicating whether the process has been stopped

    `Methods:`
        start()
            Creates a thread targeted at get(), which reads frames from CV2 VideoCapture
        get()
            Continuously gets frames from CV2 VideoCapture and sets them as self.frame attribute
        get_video_dimensions():
            Gets the width and height of the video stream frames
        stop_process()
            Sets the self.stopped attribute as True and kills the VideoCapture stream read
    """

    def __init__(self, src=0):
        self.stream = cv2.VideoCapture(src)
        (self.grabbed, self.frame) = self.stream.read()
        self.stopped = False

    def start(self):
        """
        Creates a thread targeted at get(), which reads frames from CV2 VideoCapture

        :return: self
        """
        Thread(target=self.get, args=()).start()
        return self

    def get(self):
        """
        Continuously gets frames from CV2 VideoCapture and sets them as self.frame attribute
        """
        while not self.stopped:
            (self.grabbed, self.frame) = self.stream.read()

    def get_video_dimensions(self):
        """
        Gets the width and height of the video stream frames

        :return: height `int` and width `int` of VideoCapture
        """
        width = self.stream.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = self.stream.get(cv2.CAP_PROP_FRAME_HEIGHT)
        return int(width), int(height)

    def stop_process(self):
        """
        Sets the self.stopped attribute as True and kills the VideoCapture stream read
        """
        self.stopped = True

class TruckDetection:

    def __init__(self):
        self.model = YOLO(".\yolov8m.pt")
        self.stopped = False
        self.exchange = None
    
    def start(self):
        """
        Creates a thread targeted at the ocr process
        :return: self
        """
        Thread(target=self.yolov8, args=()).start()
        return self

    def set_exchange(self, video_stream):
        """
        Sets the self.exchange attribute with a reference to VideoStream class
        :param video_stream: VideoStream class
        """
        self.exchange = video_stream

    def stop_process(self):
        """
        Sets the self.stopped attribute to True and kills the ocr() process
        """
        self.stopped = True

    def yolov8(self):
        while not self.stopped:
            if self.exchange is not None:
                for i in range(len(self.exchange)):
                    self.frame = self.exchange[i].frame
                    self.result = self.model.predict(source=self.frame)
                    self.class_detect = self.result[0].boxes.cls.numpy()
                    if 7 not in self.class_detect:
                        pass
                    else:
                        self.query = f"INSERT INTO datatruck (TruckStatus) VALUES(%s)"
                        self.data_query = ('1',)
                        cursor.execute(self.query, self.data_query)
                        db.commit()

class OCR:
    def __init__(self):
        self.exchange = None
        self.imgCoord = []
        self.stopped = False

    def start(self):
        """
        Creates a thread targeted at the ocr process
        :return: self
        """
        Thread(target=self.ocr, args=()).start()
        return self

    def set_exchange(self, video_stream):
        """
        Sets the self.exchange attribute with a reference to VideoStream class
        :param video_stream: VideoStream class
        """
        self.exchange = video_stream

    def stop_process(self):
        """
        Sets the self.stopped attribute to True and kills the ocr() process
        """
        self.stopped = True

    def ocr(self):
        while not self.stopped:
            if self.exchange is not None:
                """
                Fungsi untuk melakukan deteksi container berdasarkan pemodelan YOLOV8 yang didapat dari Roboflow
                Hasil deteksi container akan ditentukan berdasarkan confidence yang telah ditentukan]
                Argument yang dimasukkan kedalam fungsi adalah:
                1. image -> gambar input yang akan dideteksi dengan model dari roboflow
                2. conf -> tingkat threshold confidence yang ditentukan, secara default adalah 50%
                3. overlap -> overlap threshold yang diinginkan (optional), default adalah 30%
                """
                self.frame = []
                self.result = []
                for i in range(len(self.exchange)):
                    self.f = self.exchange[i].frame
                    self.frame.append(self.f)
                    self.result.append(model.predict(self.f, confidence=50, overlap=30).json())
                self.highConf = []
                for i in range(len(self.result)):
                    self.confidence = []
                    for j in range(len(self.result[i]['predictions'])):
                        """
                        seleksi confidence sesuai threshold yang telah ditentukan berdasarkan hasil prediksi
                        """
                        if self.result[i]['predictions'][j]['confidence'] < 40/100:
                            pass
                        else:
                            self.confidence.append(j)
                    self.highConf.append(self.confidence)

                self.result_OCR = []
                for i in range(len(self.highConf)):
                    if len(self.highConf[i]) != 0:
                        self.result_text = []
                        for j in range(len(self.highConf[i])):
                            if str(self.result[i]['predictions'][self.highConf[i][j]]['class']) == "container_front":
                                self.x_up = int(self.result[i]['predictions'][self.highConf[i][j]]['x']-int(self.result[i]['predictions'][self.highConf[i][j]]['width']/2))
                                self.y_up = int(self.result[i]['predictions'][self.highConf[i][j]]['y']-int(self.result[i]['predictions'][self.highConf[i][j]]['height']/2))
                                self.x_down = int(self.result[i]['predictions'][self.highConf[i][j]]['x']+int(self.result[i]['predictions'][self.highConf[i][j]]['width']/2))
                                self.y_down = int(self.result[i]['predictions'][self.highConf[i][j]]['y']+int(self.result[i]['predictions'][self.highConf[i][j]]['height']/2))
                                self.imgCoord = [self.x_up,self.y_up,self.x_down,self.y_down]
                                if len(self.imgCoord) != 0:
                                    self.image = self.frame[i][self.imgCoord[1]:self.imgCoord[3],self.imgCoord[0]:self.imgCoord[2]]
                                    self.h = reader.readtext(self.image)
                                    self.result_text.append(self.h)
                                    if len(self.h)>1:
                                        if len(self.h[0][1])==13 and len(self.h[1][1])==4:
                                            self.code2 = self.h[1][1]
                                            self.hh = list(self.h[1][1])
                                            if self.hh[2] == '6':
                                                self.hh[2] = 'G'
                                                self.code2 = "".join(self.hh)
                                            print(f"Do OCR, Camera {i}{len(self.highConf)}:",self.h[1][1], len(self.h[1][1]))
                                            self.query = f"""INSERT INTO dataocr (CameraSource, Code1, Code2)
                                                            SELECT * FROM (SELECT %s, %s, %s) AS temp
                                                            WHERE NOT EXISTS (
                                                                SELECT code1 FROM dataocr WHERE Code1 = %s
                                                            ) LIMIT 1;"""
                                            self.data_query = (str(i),self.h[0][1],self.code2,self.h[0][1])
                                            cursor.execute(self.query, self.data_query)
                                            db.commit()

