import ctypes
import subprocess

def enable_privilege(privilege):
    h_token = ctypes.c_void_p()
    ctypes.windll.kernel32.OpenProcessToken(ctypes.windll.kernel32.GetCurrentProcess(), 0x0020, ctypes.byref(h_token))

    luid = ctypes.c_long()
    ctypes.windll.advapi32.LookupPrivilegeValueW(None, privilege, ctypes.byref(luid))

    class TOKEN_PRIVILEGES(ctypes.Structure):
        _fields_ = [("PrivilegeCount", ctypes.c_ulong),
                    ("Privileges", ctypes.c_ulong * 2)]

    tkp = TOKEN_PRIVILEGES()
    tkp.PrivilegeCount = 1
    tkp.Privileges[0] = luid.value
    tkp.Privileges[1] = 0x00000002  # SePrivilegeEnabled

    ctypes.windll.advapi32.AdjustTokenPrivileges(h_token, False, ctypes.byref(tkp), 0, None, None)

def execute_as_system():
    # Run whoami command as SYSTEM using cmd
    subprocess.run(["cmd.exe", "/c", "whoami"], shell=True)

if __name__ == "__main__":
    enable_privilege("SeImpersonatePrivilege")
    execute_as_system()
