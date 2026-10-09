import socket
import struct
import cv2
import numpy as np
import pyvirtualcam
import sys
import subprocess
import time
import threading
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QComboBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor

def create_monochrome_icon():
    # Draws a sleek, pure black and white minimalist camera icon dynamically
    pixmap = QPixmap(64, 64)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    
    # White background circle
    painter.setBrush(QColor("#FFFFFF"))
    painter.setPen(Qt.NoPen)
    painter.drawEllipse(2, 2, 60, 60)
    
    # Black Camera Body
    painter.setBrush(QColor("#000000"))
    painter.drawRoundedRect(12, 22, 40, 26, 4, 4)
    
    # Camera Flash/Top part
    painter.drawRoundedRect(24, 16, 16, 10, 2, 2)
    
    # White Lens
    painter.setBrush(QColor("#FFFFFF"))
    painter.drawEllipse(22, 25, 20, 20)
    
    # Black Inner Lens
    painter.setBrush(QColor("#000000"))
    painter.drawEllipse(27, 30, 10, 10)
    
    painter.end()
    return QIcon(pixmap)

class WindowsUSBWebcamClient(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("USC-CAM | 4K Host")
        self.setFixedSize(450, 300)
        self.setWindowIcon(create_monochrome_icon())
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0A0A0A;
            }
            QLabel {
                color: #FFFFFF;
                font-family: 'Segoe UI', Inter, sans-serif;
            }
            QLabel#Title {
                font-size: 24px;
                font-weight: bold;
                letter-spacing: 2px;
            }
            QLabel#Status {
                font-size: 12px;
                color: #888888;
                font-weight: 600;
                letter-spacing: 1px;
            }
            QComboBox {
                background-color: #1A1A1A;
                color: #FFFFFF;
                border: 1px solid #333333;
                border-radius: 6px;
                padding: 10px 15px;
                font-size: 14px;
                font-weight: bold;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #1A1A1A;
                color: #FFFFFF;
                selection-background-color: #333333;
                border: 1px solid #333333;
            }
        """)
        
        self.init_ui()
        self.start_usbmuxd_proxy()
        
        # Start stream in background thread so UI stays smooth
        self.stream_thread = threading.Thread(target=self.stream_loop, daemon=True)
        self.stream_thread.start()
        
    def init_ui(self):
        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(25)
        
        # Title
        title_label = QLabel("USC-CAM STUDIO")
        title_label.setObjectName("Title")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Status Label
        self.status_label = QLabel("INITIALIZING USB CONNECTION...")
        self.status_label.setObjectName("Status")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Resolution Dropdown
        self.res_select = QComboBox()
        self.res_select.addItems(["3840x2160  ( 4K UHD )", "2560x1440  ( QHD )", "1920x1080  ( FHD )"])
        self.res_select.setCursor(Qt.PointingHandCursor)
        layout.addWidget(self.res_select)
        
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def start_usbmuxd_proxy(self):
        try:
            subprocess.Popen(["iproxy", "9999", "9999"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.status_label.setText("USB PROXY ACTIVE | WAITING FOR FEED")
        except Exception as e:
            self.status_label.setText("USB ERROR | PLEASE RECONNECT IPHONE")

    def stream_loop(self):
        while True:
            try:
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client.connect(('127.0.0.1', 9999))
                self.status_label.setText("LIVE 4K STREAM RUNNING")
                
                with pyvirtualcam.Camera(width=3840, height=2160, fps=30, fmt=pyvirtualcam.PixelFormat.BGR) as cam:
                    payload_size = struct.calcsize(">I")
                    data = b""
                    
                    while True:
                        while len(data) < payload_size:
                            packet = client.recv(4096)
                            if not packet:
                                break
                            data += packet
                        if not data: break
                        
                        packed_msg_size = data[:payload_size]
                        data = data[payload_size:]
                        msg_size = struct.unpack(">I", packed_msg_size)[0]
                        
                        while len(data) < msg_size:
                            data += client.recv(4096)
                        
                        frame_data = data[:msg_size]
                        data = data[msg_size:]
                        
                        np_arr = np.frombuffer(frame_data, np.uint8)
                        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
                        
                        if frame is not None:
                            cam.send(frame)
                            cam.sleep_until_next_frame()
            except Exception as e:
                time.sleep(2)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = WindowsUSBWebcamClient()
    window.show()
    sys.exit(app.exec_())
