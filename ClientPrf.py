from PyQt5 import QtCore, QtWidgets
import Prof

import sys
import socket
import random


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


class ClientPrf(object):
    def __init__(self):
        self.messages = []
        self.mainWindow = QtWidgets.QMainWindow()

        # add widgets to the application window
        self.ProfWidget = QtWidgets.QWidget(self.mainWindow)

        self.Prof = Prof.Ui_Form()
        self.Prof.setupUi(self.ProfWidget)
        self.Prof.connectButton.clicked.connect(self.btn_connect_clicked)
        self.Prof.sendButton.clicked.connect(self.send_message)
        self.Prof.decButton.clicked.connect(self.retour)
        self.mainWindow.setGeometry(QtCore.QRect(50, 50,650, 445))
        self.mainWindow.setWindowTitle("Enseignant")
        self.mainWindow.show()

        self.tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def retour(self):
        self.mainWindow.close()
    
    def btn_connect_clicked(self):
        host = self.Prof.hostTextEdit.toPlainText()
        port = self.Prof.portTextEdit.toPlainText()
        nickname = self.Prof.nameTextEdit.toPlainText()

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
            nickname = socket.gethostname()

        nickname = nickname

        if self.connect(host, port, nickname):
            self.recv_thread = ReceiveThread(self.tcp_client)
            self.recv_thread.signal.connect(self.show_message)
            self.recv_thread.start()
            print("[INFO] recv thread started")


    def show_message(self, message):
        self.Prof.messageBrowser.append(message)
        

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
            self.Prof.hostTextEdit.clear()
            self.Prof.portTextEdit.clear()
            
            return False
        

    def send_message(self):
        message = self.Prof.msgTextEdit.toPlainText()
        self.Prof.messageBrowser.append("Me: " + message)

        print("sent: " + message)

        try:
            self.tcp_client.send(message.encode())
        except Exception as e:
            error = "Unable to send message '{}'".format(str(e))
            print("[INFO]", error)
            self.show_error("Server Error", error)
        self.Prof.msgTextEdit.clear()


    def show_error(self, error_type, message):
        errorDialog = QtWidgets.QMessageBox()
        errorDialog.setText(message)
        errorDialog.setWindowTitle(error_type)
        errorDialog.setStandardButtons(QtWidgets.QMessageBox.Ok)
        errorDialog.exec_()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    c = ClientPrf()
    sys.exit(app.exec())