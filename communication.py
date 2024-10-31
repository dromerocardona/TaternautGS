import threading
import serial
import csv


class Communication:

    def __init__(self, serial_port, baud_rate=9600, timeout=4, csv_filename='taternauts.csv'):
        self.serial_port = serial_port
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.data_list = []
        self.reading = False
        self.csv_filename = csv_filename

        with open(self.csv_filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Team_Number", "Time", "PacketCount", "SW_STATE", "PL_STATE", "Altitude",
                             "Temperature", "Voltage", "GYRO_R", "GYRO_P", "GYRO_Y", "Pressure", "POTATO"])

    def read(self, signal_emitter):
        self.reading = True
        with serial.Serial(self.serial_port, self.baud_rate, timeout=self.timeout) as ser:
            print("Port opened successfully!")
            with open(self.csv_filename, mode='a', newline='') as file:
                writer = csv.writer(file)
                while self.reading:
                    try:
                        line = ser.read_until(b'POTATO').decode('utf-8').strip()
                        if line:
                            print(f"Received: {line}")
                            self.parse_csv_data(line)
                            signal_emitter.emit_signal()
                            writer.writerow(line.split(','))
                    except Exception as e:
                        print(f"Error: {e}")

    def stop_reading(self):
        self.reading = False

    def parse_csv_data(self, data):
        csv_data = data.split(',')
        self.data_list.append(csv_data)

    def get_data(self):
        return self.data_list

    def getTime(self):
        if self.data_list:
            try:
                return self.data_list[-1][1]
            except (IndexError, ValueError):
                return None
        return None

    def getPacketCount(self):
        if self.data_list:
            try:
                return self.data_list[-1][2]
            except (IndexError, ValueError):
                return None
        return None

    def getSW_STATE(self):
        if self.data_list:
            try:
                return self.data_list[-1][3]
            except (IndexError, ValueError):
                return None
        return None

    def getPL_STATE(self):
        if self.data_list:
            try:
                return self.data_list[-1][4]
            except (IndexError, ValueError):
                return None
        return None

    def getAltitude(self):
        if self.data_list:
            try:
                return float(self.data_list[-1][5])
            except (IndexError, ValueError):
                return None
        return None

    def getTemperature(self):
        if self.data_list:
            try:
                return float(self.data_list[-1][6])
            except (IndexError, ValueError):
                return None
        return None

    def getVoltage(self):
        if self.data_list:
            try:
                return float(self.data_list[-1][7])
            except (IndexError, ValueError):
                return None
        return None

    def getGYRO_R(self):
        if self.data_list:
            try:
                return float(self.data_list[-1][8])
            except (IndexError, ValueError):
                return None
        return None

    def getGYRO_P(self):
        if self.data_list:
            try:
                return float(self.data_list[-1][9])
            except (IndexError, ValueError):
                return None
        return None

    def getGYRO_Y(self):
        if self.data_list:
            try:
                return float(self.data_list[-1][10])
            except (IndexError, ValueError):
                return None
        return None

    def getPressure(self):
        if self.data_list:
            try:
                return float(self.data_list[-1][11])
            except (IndexError, ValueError):
                return None
        return None
