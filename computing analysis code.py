import serial
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime

arduino_port = "COM3"
ser = serial.Serial(arduino_port, 9600, timeout=1)

v1_ham = []
v2_ham = []
zamanlar = []

print(">>> Logging started...")
print(">>> To stop, perform the command Ctrl+C")

with open("log.txt", "a") as log_dosyasi:
    log_dosyasi.write(f"\n--- New Logging Sequence: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n")
    log_dosyasi.write("Date_Time,Panel1_V,Panel2_V\n")

    try:
        while True:
            line = ser.readline().decode('utf-8').strip()
            if line:
                try:
                    val1, val2 = map(float, line.split(','))
                    su_an = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                    v1_ham.append(val1)
                    v2_ham.append(val2)
                    zamanlar.append(su_an)

                    log_satiri = f"{su_an},{val1},{val2}\n"
                    log_dosyasi.write(log_satiri)
                    log_dosyasi.flush()

                    print(f"[{su_an}] Logged: {val1}V, {val2}V")
                except ValueError:
                    continue
    except KeyboardInterrupt:
        print("\n>>> Logging stopped. <Creating graphs...")
    finally:
        ser.close()


if len(v1_ham) > 0:
    df = pd.DataFrame({'v1': v1_ham, 'v2': v2_ham})
    v1_ortalama = df['v1'].rolling(window=5, min_periods=1).mean()
    v2_ortalama = df['v2'].rolling(window=5, min_periods=1).mean()

    plt.figure(figsize=(12, 6))
    plt.subplot(2, 1, 1)
    plt.plot(v1_ham, alpha=0.3, color='blue', label='Raw P1')
    plt.plot(v1_ortalama, color='blue', linewidth=2, label='Average P1')
    plt.title("Panel 1 Log")
    plt.legend()

    plt.subplot(2, 1, 2)
    plt.plot(v2_ham, alpha=0.3, color='orange', label='Raw P2')
    plt.plot(v2_ortalama, color='orange', linewidth=2, label='Average P2')
    plt.xlabel("Log Series")
    plt.legend()

    plt.tight_layout()
    plt.show()