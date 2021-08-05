
from PyQt5 import QtCore, QtGui, QtWidgets
from tensorflow.python.ops.gen_math_ops import mod
import etudiant
#import client_ui
#import connect_ui

import sys
import socket
import random
from Server import Server
import cv2
import tensorflow as tf
import numpy as np




class ReceiveThread(QtCore.QThread):
    signal = QtCore.pyqtSignal(str)

    def __init__(self, client_socket):
        super(ReceiveThread, self).__init__()
        self.client_socket = client_socket

    def run(self):
        while True:
            self.receive_message()

    def receive_message(self):
        message = self.client_socket.recv(1024)
        message = message.decode()

        print(message)
        self.signal.emit(message)


class Client(object):
    def __init__(self):
        self.messages = []
        self.mainWindow = QtWidgets.QMainWindow()
        self.emo = ""
        # add widgets to the application window
        self.EtudiantWidget = QtWidgets.QWidget(self.mainWindow)

        self.Etudiant = etudiant.Ui_Etuiant()
        self.Etudiant.setupUi(self.EtudiantWidget)
        self.Etudiant.connectButton.clicked.connect(self.btn_connect_clicked)
        self.Etudiant.sendButton.clicked.connect(self.send_message)
        self.Etudiant.decButton.clicked.connect(self.retour)
        self.Etudiant.VideoButton.clicked.connect(self.VideoOpen)

        self.mainWindow.setGeometry(QtCore.QRect(50, 50,750, 516))
        self.mainWindow.setWindowTitle("Etudiant")
        self.mainWindow.show()

        self.tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        
    def btn_connect_clicked(self):
        host = self.Etudiant.hostTextEdit.toPlainText()
        port = self.Etudiant.portTextEdit.toPlainText()
        nickname = self.Etudiant.nameTextEdit.toPlainText()
        print("Amsii yaw : ", nickname)

        if len(host) == 0:
            host = "localhost"
        
        if len(port) == 0:
            port = 5555
        else:
            try:
                port = int(port)
            except Exception as e:
                error = "Invalid port number \n'{}'".format(str(e))
                print("[INFO]", error)
                self.show_error("Port Number Error", error)
        
        if len(nickname) < 1:
            print("Len = ",len(nickname))
            nickname = socket.gethostname()
            print("Nikname : ",nickname)

        nickname = nickname

        if self.connect(host, port, nickname):
            self.recv_thread = ReceiveThread(self.tcp_client)
            self.recv_thread.signal.connect(self.show_message)
            self.recv_thread.start()
            print("[INFO] recv thread started")


    def show_message(self, message):
        self.Etudiant.messageBrowser.append(message)
    #-------------
    def retour(self):
        self.mainWindow.close()
    #-------------
    def connect(self, host, port, nickname):
        
        try:
            self.tcp_client.connect((host, port))
            self.tcp_client.send(nickname.encode())

            print("[INFO] Connected to server")

            return True
        except Exception as e:
            error = "Unable to connect to server \n'{}'".format(str(e))
            print("[INFO]", error)
            self.show_error("Connection Error", error)
            self.Etudiant.hostTextEdit.clear()
            self.Etudiant.portTextEdit.clear()
            
            return False
        

    def send_message(self):
        message = self.Etudiant.msgTextEdit.toPlainText()
        self.Etudiant.messageBrowser.append("Me: " + message)

        print("sent: " + message)

        try:
            self.tcp_client.send(message.encode())
        except Exception as e:
            error = "Unable to send message '{}'".format(str(e))
            print("[INFO]", error)
            self.show_error("Server Error", error)
        self.Etudiant.msgTextEdit.clear()
    # Pour les emotions
    def send_emo(self, e):
        
        #self.Etudiant.messageBrowser.append("Me: " + e)

        print("sent: " + e)

        try:
            self.tcp_client.send(e.encode())
        except Exception as e:
            error = "Unable to send emotion '{}'".format(str(e))
            print("[INFO]", error)
            self.show_error("Server Error", error)
        e = ""
              


    def show_error(self, error_type, message):
        errorDialog = QtWidgets.QMessageBox()
        errorDialog.setText(message)
        errorDialog.setWindowTitle(error_type)
        errorDialog.setStandardButtons(QtWidgets.QMessageBox.Ok)
        errorDialog.exec_()
    
    
    def VideoOpen(self):
        model = self.LoadModel()
        emotions = ['Colere', 'Degoute', 'Peur', 'Heureux', 'Triste', 'Surpris', 'Neutre']
        cascPath = 'haarcascade_frontalface_alt.xml'
        faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + cascPath)
        video_capture = cv2.VideoCapture(0)
        
        t = 1
        tmax = 1
        while True:
            if not video_capture.isOpened():	
                print("Impossible d'ouvrir la caméra")
            else:
                ret, frame = video_capture.read()						
                gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)	

                faces = faceCascade.detectMultiScale(
                gray_frame,
                scaleFactor	= 1.1,
                minNeighbors= 5,
                minSize	= (30, 30))

                prediction = None
                x, y = None, None

                for (x, y, w, h) in faces:
                    ROI_gray = gray_frame[y:y+h, x:x+w] 
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
                    with tf.device("/CPU:0"):
                        emotion = self.preprocess_input(ROI_gray)
                        prediction = model.predict(emotion)
                        print(prediction[0][0])
                        top_1_prediction = emotions[np.argmax(prediction)]
                        self.emo = top_1_prediction
                        self.send_emo(self.emo)
                        print("time : ",t)
                        
                        
                        
                        
                    cv2.putText(frame, top_1_prediction, (x, y+(h+50)), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 4, cv2.LINE_AA)
                frame = cv2.resize(frame, (800, 500))
                cv2.imshow('Video', frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break


        video_capture.release()
        cv2.destroyAllWindows()
    # Pour charger le modele
    def LoadModel(self):
        return tf.keras.models.load_model('ResNet-50.h5')
    # Pour appliquer les transformation necessaire pour utiliser le modele
    def preprocess_input(self,image):
        img_width = 197
        img_height = 197
        image = cv2.resize(image, (img_width, img_height))  # redimensionner les images
        ret = np.empty((img_height, img_width, 3)) # creer un tableau vide
        ret[:, :, 0] = image
        ret[:, :, 1] = image
        ret[:, :, 2] = image

        #print("Ret = ", ret)
        x = np.expand_dims(ret, axis = 0)   # (1, XXX, XXX, 3)
    
        x -= 128.8006   
        x /= 64.6497    
        return x

    

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    c = Client()
    sys.exit(app.exec())