import os
import sys
import ctypes

# تحقق من تمرير الأمر
if len(sys.argv) < 2:
    print("Usage: python xa.py <command>")
    sys.exit(1)

# دالة لتمكين الامتياز
def enable_privilege(privilege_name):
    h_token = ctypes.c_void_p()
    ctypes.windll.kernel32.OpenProcessToken(ctypes.windll.kernel32.GetCurrentProcess(), 0x0020, ctypes.byref(h_token))
    
    luid = ctypes.c_void_p()
    ctypes.windll.advapi32.LookupPrivilegeValueW(None, privilege_name, ctypes.byref(luid))
    
    tkp = ctypes.c_void_p()
    ctypes.windll.advapi32.AdjustTokenPrivileges(h_token, False, ctypes.byref(luid), 0, None, None)

# تمكين SeImpersonatePrivilege
enable_privilege("SeImpersonatePrivilege")

# تنفيذ الأمر الممرر كمسؤول
command = sys.argv[1]
os.system(command)
