import os
import ctypes
import sys

if len(sys.argv) < 2:
    print("Usage: python script.py <command>")
    sys.exit(1)

# Get the current process token
token = ctypes.c_void_p()
ctypes.windll.kernel32.OpenProcessToken(ctypes.windll.kernel32.GetCurrentProcess(), 0x0020, ctypes.byref(token))

# Set the privilege to SeImpersonatePrivilege
SE_IMPERSONATE_NAME = "SeImpersonatePrivilege"
luid = ctypes.c_void_p()

# Lookup the privilege
ctypes.windll.advapi32.LookupPrivilegeValueW(None, SE_IMPERSONATE_NAME, ctypes.byref(luid))

# Enable the privilege
tkp = ctypes.c_void_p()
tkpPrivilege = ctypes.create_string_buffer(8)
tkpPrivilege = ctypes.cast(tkpPrivilege, ctypes.POINTER(ctypes.c_void_p))
ctypes.windll.advapi32.SetTokenInformation(token, 20, ctypes.byref(luid), 0)

# Run the command as an administrator
command = sys.argv[1]
os.system(command)
