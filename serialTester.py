import serial

try:
    serial_port = "COM8"
    baud_rate = 9600
    with serial.Serial(serial_port, baud_rate, timeout=2) as ser:
        print("Port opened successfully!")
        while True:
            line = ser.read_until(b'POTATO').decode('utf-8').strip()
            if line:
                if line.startswith("1002"):
                    print(f"Received: {line}")
except serial.SerialException as e:
    print(f"Error: {e}")


