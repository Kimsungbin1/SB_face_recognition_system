import sys
import cv2
import numpy as np
import face_recognition
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QFileDialog, QInputDialog, QMessageBox
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer, Qt, QThread, pyqtSignal
import os
import pickle
import datetime
import csv
import time

class FaceRecognitionThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)

    def __init__(self, known_face_encodings, known_face_names):
        super().__init__()
        self.known_face_encodings = known_face_encodings
        self.known_face_names = known_face_names
        self._run_flag = True
        self.fps = 30
        self.frame_time = 1 / self.fps

    def run(self):
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # Reduced resolution
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        face_locations = []
        face_encodings = []
        face_names = []
        process_this_frame = True

        while self._run_flag:
            start_time = time.time()
            
            ret, frame = cap.read()
            if ret:
                if process_this_frame:
                    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
                    
                    face_locations = face_recognition.face_locations(rgb_small_frame)
                    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

                    face_names = []
                    for face_encoding in face_encodings:
                        matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
                        name = "Unknown"
                        if True in matches:
                            first_match_index = matches.index(True)
                            name = self.known_face_names[first_match_index]
                        face_names.append(name)

                process_this_frame = not process_this_frame

                for (top, right, bottom, left), name in zip(face_locations, face_names):
                    top *= 4
                    right *= 4
                    bottom *= 4
                    left *= 4

                    color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
                    cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                    cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
                    font = cv2.FONT_HERSHEY_DUPLEX
                    cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.8, (255, 255, 255), 1)

                    if name != "Unknown":
                        self.log_recognition(name)

                self.change_pixmap_signal.emit(frame)
            
            # Control frame rate
            processing_time = time.time() - start_time
            if processing_time < self.frame_time:
                time.sleep(self.frame_time - processing_time)

        cap.release()

    def stop(self):
        self._run_flag = False
        self.wait()

    def log_recognition(self, name):
        today = datetime.date.today()
        log_file = f'recognition_log_{today.strftime("%Y-%m-%d")}.csv'
        
        if not os.path.exists(log_file):
            with open(log_file, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Timestamp', 'Name'])

        with open(log_file, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), name])

class FaceRecognitionApp(QWidget):
    def __init__(self):
        super().__init__()
        self.known_face_encodings = []
        self.known_face_names = []
        self.load_known_faces()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Face Recognition System')
        self.setGeometry(100, 100, 1300, 800)

        self.image_label = QLabel(self)
        self.image_label.resize(1280, 720)

        self.start_button = QPushButton('Start', self)
        self.start_button.clicked.connect(self.start_recognition)

        self.stop_button = QPushButton('Stop', self)
        self.stop_button.clicked.connect(self.stop_recognition)
        self.stop_button.setEnabled(False)

        self.add_face_button = QPushButton('Add Face', self)
        self.add_face_button.clicked.connect(self.add_face)

        self.view_log_button = QPushButton('View Logs', self)
        self.view_log_button.clicked.connect(self.view_logs)

        vbox = QVBoxLayout()
        vbox.addWidget(self.image_label)
        vbox.addWidget(self.start_button)
        vbox.addWidget(self.stop_button)
        vbox.addWidget(self.add_face_button)
        vbox.addWidget(self.view_log_button)

        self.setLayout(vbox)

    def start_recognition(self):
        self.thread = FaceRecognitionThread(self.known_face_encodings, self.known_face_names)
        self.thread.change_pixmap_signal.connect(self.update_image)
        self.thread.start()
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    def stop_recognition(self):
        self.thread.stop()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def update_image(self, cv_img):
        qt_img = self.convert_cv_qt(cv_img)
        self.image_label.setPixmap(qt_img)

    def convert_cv_qt(self, cv_img):
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.image_label.width(), self.image_label.height(), Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)

    def add_face(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Image Files (*.png *.jpg *.jpeg)")
        if file_name:
            name, ok = QInputDialog.getText(self, "Input Name", "Enter the name of the person:")
            if ok and name:
                try:
                    image = face_recognition.load_image_file(file_name)
                    encoding = face_recognition.face_encodings(image)[0]
                    self.known_face_encodings.append(encoding)
                    self.known_face_names.append(name)
                    self.save_known_faces()
                    QMessageBox.information(self, "Success", f"Face of {name} added successfully!")
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Failed to add face: {str(e)}")

    def load_known_faces(self):
        if os.path.exists('known_faces.pkl'):
            try:
                with open('known_faces.pkl', 'rb') as f:
                    data = pickle.load(f)
                    self.known_face_encodings = data['encodings']
                    self.known_face_names = data['names']
            except Exception as e:
                print(f"Error loading known faces: {str(e)}")

    def save_known_faces(self):
        try:
            with open('known_faces.pkl', 'wb') as f:
                pickle.dump({
                    'encodings': self.known_face_encodings,
                    'names': self.known_face_names
                }, f)
        except Exception as e:
            print(f"Error saving known faces: {str(e)}")

    def view_logs(self):
        today = datetime.date.today()
        log_file = f'recognition_log_{today.strftime("%Y-%m-%d")}.csv'
        
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r') as f:
                    log_content = f.read()
                QMessageBox.information(self, "Today's Logs", log_content)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to read log file: {str(e)}")
        else:
            QMessageBox.information(self, "No Logs", "No logs found for today.")

    def closeEvent(self, event):
        if hasattr(self, 'thread'):
            self.thread.stop()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = FaceRecognitionApp()
    ex.show()
    sys.exit(app.exec_())