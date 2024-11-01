import os
import sys
import ctypes

def enable_privilege(privilege_name):
    """Enable the specified privilege."""
    h_token = ctypes.c_void_p()
    ctypes.windll.kernel32.OpenProcessToken(ctypes.windll.kernel32.GetCurrentProcess(), 0x0020, ctypes.byref(h_token))

    luid = ctypes.c_void_p()
    ctypes.windll.advapi32.LookupPrivilegeValueW(None, privilege_name, ctypes.byref(luid))

    tkp = ctypes.c_void_p()
    ctypes.windll.advapi32.AdjustTokenPrivileges(h_token, False, ctypes.byref(luid), 0, None, None)

def main():
    # Enable the SeImpersonatePrivilege
    enable_privilege("SeImpersonatePrivilege")

    # Execute the whoami command as an administrator
    os.system("whoami")

if __name__ == "__main__":
    main()
