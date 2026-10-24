import sys
import time
import serial

# Adjust port according to your system (/dev/ttyACM0, /dev/ttyUSB0, etc.)
PORT = "/dev/ttyUSB0"
BAUD = 115200


def send_command(cmd):
  try:
    with serial.Serial(PORT, BAUD, timeout=2) as ser:
      time.sleep(2)  # Wait for Arduino auto-reset
      ser.write(f"{cmd}\n".encode("utf-8"))
      response = ser.readline().decode("utf-8").strip()
      print(f"Arduino Response: {response}")
  except Exception as e:
    print(f"Error communicating with Arduino: {e}")


if __name__ == "__main__":
  if len(sys.argv) > 1:
    send_command(sys.argv[1])
  else:
    print("No command provided.")
