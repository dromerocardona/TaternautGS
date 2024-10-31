import sys
import threading
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton, \
    QSpacerItem, QSizePolicy, QGridLayout
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QTimer
from PyQt5.QtGui import QFont, QPixmap, QIcon
from communication import Communication
from pressureGraph import PressureGraph
from temperatureGraph import TemperatureGraph
from altitudeGraph import AltitudeGraph
from rotationGraph import RotationGraph
from voltageGraph import VoltageGraph
from time import time


class SignalEmitter(QObject):
    update_signal = pyqtSignal()

    def emit_signal(self):
        self.update_signal.emit()


class GroundStation(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Taternauts GS")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("""
            QMainWindow {
                background-image: url("C:/Users/lukes/Downloads/gsBackground.jpg");
                background-repeat: no-repeat;
                background-position: center;
                background-size: cover;
            }
        """)
        self.setWindowIcon(QIcon('C:/Users/lukes/Downloads/potat.png'))

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        main_layout = QVBoxLayout(self.central_widget)

        header_layout = QHBoxLayout()

        # Add header text
        header_text = QLabel("TATERNAUTS GROUND STATION")
        header_text.setAlignment(Qt.AlignCenter)
        header_text.setFont(QFont("Georgia", 24, QFont.Bold))
        header_text.setStyleSheet("color: white;")
        header_layout.addWidget(header_text)

        header_widget = QWidget()
        header_widget.setLayout(header_layout)
        main_layout.addWidget(header_widget)

        content_layout = QHBoxLayout()

        # Sidebar
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setAlignment(Qt.AlignTop)
        sidebar_layout.setSpacing(10)

        sidebar_layout.addItem(QSpacerItem(10, 10))

        logo_pixmap = QPixmap("C:/Users/lukes/Downloads/potat.png")
        logo_width, logo_height = 100, 100
        logo_pixmap = logo_pixmap.scaled(logo_width, logo_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_label = QLabel()
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(logo_label)

        team_ID = QLabel("Team ID: 1002")
        team_ID.setAlignment(Qt.AlignCenter)
        team_ID.setFont(QFont("Georgia", 14))
        team_ID.setStyleSheet("color: white;")
        sidebar_layout.addWidget(team_ID)

        # Add reset button
        reset_button = QPushButton("Reset")
        reset_button.setFont(QFont("Arial", 14))
        reset_button.clicked.connect(self.reset_graphs)
        sidebar_layout.addWidget(reset_button)

        # Add a start/stop button
        self.start_stop_button = QPushButton("Start")
        self.start_stop_button.setFont(QFont("Arial", 14))
        self.start_stop_button.clicked.connect(self.toggle_data_transmission)
        sidebar_layout.addWidget(self.start_stop_button)

        # Labels for live data
        self.liveTime = QLabel("Time Elapsed: N/A")
        self.liveTime.setStyleSheet("color: white;")
        self.livePacketCount = QLabel("Packet Count: N/A")
        self.livePacketCount.setStyleSheet("color: white;")
        self.liveSW_STATE = QLabel("SW_STATE: N/A")
        self.liveSW_STATE.setStyleSheet("color: white;")
        self.livePL_STATE = QLabel("PL_STATE: N/A")
        self.livePL_STATE.setStyleSheet("color: white;")

        # Add live data labels to sidebar
        sidebar_layout.addWidget(self.liveTime)
        sidebar_layout.addWidget(self.livePacketCount)
        sidebar_layout.addWidget(self.liveSW_STATE)
        sidebar_layout.addWidget(self.livePL_STATE)

        sidebar_layout.addItem(QSpacerItem(10, 300))
        self.copyright = QLabel("Taternauts © 2024")
        self.copyright.setAlignment(Qt.AlignCenter)
        self.copyright.setFont(QFont("Georgia", 10))
        self.copyright.setStyleSheet("color: white;")
        sidebar_layout.addWidget(self.copyright)

        # Setup graphs
        graphs_layout = QVBoxLayout()
        graphs_grid = QGridLayout()

        self.pressureGraph = PressureGraph()
        self.temperatureGraph = TemperatureGraph()
        self.rotationGraph = RotationGraph()
        self.voltageGraph = VoltageGraph()
        self.altitudeGraph = AltitudeGraph()

        graphs_grid.addWidget(self.pressureGraph.win, 0, 0)
        graphs_grid.addWidget(self.temperatureGraph.win, 0, 1)
        graphs_grid.addWidget(self.altitudeGraph.win, 1, 0)
        graphs_grid.addWidget(self.rotationGraph.win, 1, 1)
        graphs_grid.addWidget(self.voltageGraph.win, 2, 0)

        graphs_layout.addLayout(graphs_grid)

        self.comm = Communication(serial_port='COM8')

        self.reader_thread = None
        self.reading_data = False

        self.signal_emitter = SignalEmitter()
        self.signal_emitter.update_signal.connect(self.update_graphs)

        # Add the sidebar and main content layout to the content layout
        content_layout.addLayout(sidebar_layout)
        content_layout.addLayout(graphs_layout)

        # Add content layout to the main layout
        main_layout.addLayout(content_layout)

        # Setup a QTimer to update live data periodically
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_live_data)
        self.timer.start(1000)  # Update every second

    def toggle_data_transmission(self):
        if self.reading_data:
            self.stop_data_transmission()
        else:
            self.start_data_transmission()

    def start_data_transmission(self):
        self.reading_data = True
        self.start_stop_button.setText("Stop")
        self.reader_thread = threading.Thread(target=self.comm.read, args=(self.signal_emitter,))
        self.reader_thread.start()

    def stop_data_transmission(self):
        self.reading_data = False
        self.start_stop_button.setText("Start")
        if self.reader_thread and self.reader_thread.is_alive():
            self.comm.stop_reading()
            self.reader_thread.join()
            self.reader_thread = None

    def update_live_data(self):
        self.liveTime.setText(f"Time Elapsed: {self.comm.getTime() or 'N/A'}")
        self.livePacketCount.setText(f"Packet Count: {self.comm.getPacketCount() or 'N/A'}")
        self.liveSW_STATE.setText(f"SW_STATE: {self.comm.getSW_STATE() or 'N/A'}")
        self.livePL_STATE.setText(f"PL_STATE: {self.comm.getPL_STATE() or 'N/A'}")

    def update_graphs(self):
        current_time = time()

        pressure = self.comm.getPressure()
        if pressure is not None:
            self.pressureGraph.update_graph(pressure, current_time)

        temperature = self.comm.getTemperature()
        if temperature is not None:
            self.temperatureGraph.update_graph(temperature, current_time)

        altitude = self.comm.getAltitude()
        if altitude is not None:
            self.altitudeGraph.update_graph(altitude, current_time)

        gyro_r = self.comm.getGYRO_R()
        gyro_p = self.comm.getGYRO_P()
        gyro_y = self.comm.getGYRO_Y()
        if gyro_r is not None and gyro_p is not None and gyro_y is not None:
            self.rotationGraph.update_graph(gyro_r, gyro_p, gyro_y, current_time)

        voltage = self.comm.getVoltage()
        if voltage is not None:
            self.voltageGraph.update_graph(voltage, current_time)

    def reset_graphs(self):
        self.pressureGraph.reset_graph()
        self.temperatureGraph.reset_graph()
        self.altitudeGraph.reset_graph()
        self.rotationGraph.reset_graph()
        self.voltageGraph.reset_graph()

    def closeEvent(self, event):
        self.stop_data_transmission()
        super().closeEvent(event)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = GroundStation()
    window.show()
    app.exec_()
