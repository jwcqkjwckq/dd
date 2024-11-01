''' Windows Helpers For Tests '''

import contextlib
import ctypes
import functools
import unittest

from ctypes import wintypes

__all__ = (
    'acquire_privilege',
    'adjust_privileges',
    'disable_privilege',
    'enable_privilege',
    'skip_unless_privilege',
)

kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
advapi32 = ctypes.WinDLL('advapi32', use_last_error=True)

ERROR_NOT_ALL_ASSIGNED = 1300

SE_PRIVILEGE_ENABLED_BY_DEFAULT = 0x00000001
SE_PRIVILEGE_ENABLED = 0x00000002
SE_PRIVILEGE_REMOVED = 0x00000004
SE_PRIVILEGE_USED_FOR_ACCESS = 0x80000000

TOKEN_QUERY = 0x0008
TOKEN_ADJUST_PRIVILEGES = 0x0020

SE_ASSIGNPRIMARYTOKEN_NAME = "SeAssignPrimaryTokenPrivilege"
SE_AUDIT_NAME = "SeAuditPrivilege"
SE_BACKUP_NAME = "SeBackupPrivilege"
SE_CHANGE_NOTIFY_NAME = "SeChangeNotifyPrivilege"
SE_CREATE_GLOBAL_NAME = "SeCreateGlobalPrivilege"
SE_CREATE_PAGEFILE_NAME = "SeCreatePagefilePrivilege"
SE_CREATE_PERMANENT_NAME = "SeCreatePermanentPrivilege"
SE_CREATE_SYMBOLIC_LINK_NAME = "SeCreateSymbolicLinkPrivilege"
SE_CREATE_TOKEN_NAME = "SeCreateTokenPrivilege"
SE_DEBUG_NAME = "SeDebugPrivilege"
SE_DELEGATE_SESSION_USER_IMPERSONATE_NAME = (
    "SeDelegateSessionUserImpersonatePrivilege")

SE_ENABLE_DELEGATION_NAME = "SeEnableDelegationPrivilege"
SE_IMPERSONATE_NAME = "SeImpersonatePrivilege"
SE_INCREASE_QUOTA_NAME = "SeIncreaseQuotaPrivilege"
SE_INC_BASE_PRIORITY_NAME = "SeIncreaseBasePriorityPrivilege"
SE_INC_WORKING_SET_NAME = "SeIncreaseWorkingSetPrivilege"
SE_LOAD_DRIVER_NAME = "SeLoadDriverPrivilege"
SE_LOCK_MEMORY_NAME = "SeLockMemoryPrivilege"
SE_MACHINE_ACCOUNT_NAME = "SeMachineAccountPrivilege"
SE_MANAGE_VOLUME_NAME = "SeManageVolumePrivilege"
SE_PROF_SINGLE_PROCESS_NAME = "SeProfileSingleProcessPrivilege"

SE_RELABEL_NAME = "SeRelabelPrivilege"
SE_REMOTE_SHUTDOWN_NAME = "SeRemoteShutdownPrivilege"
SE_RESTORE_NAME = "SeRestorePrivilege"
SE_SECURITY_NAME = "SeSecurityPrivilege"
SE_SHUTDOWN_NAME = "SeShutdownPrivilege"
SE_SYNC_AGENT_NAME = "SeSyncAgentPrivilege"
SE_SYSTEMTIME_NAME = "SeSystemtimePrivilege"
SE_SYSTEM_ENVIRONMENT_NAME = "SeSystemEnvironmentPrivilege"
SE_SYSTEM_PROFILE_NAME = "SeSystemProfilePrivilege"

SE_TAKE_OWNERSHIP_NAME = "SeTakeOwnershipPrivilege"
SE_TCB_NAME = "SeTcbPrivilege"
SE_TIME_ZONE_NAME = "SeTimeZonePrivilege"
SE_TRUSTED_CREDMAN_ACCESS_NAME = "SeTrustedCredManAccessPrivilege"
SE_UNDOCK_NAME = "SeUndockPrivilege"


class LUID(ctypes.Structure):
    __slots__ = ()
    _fields_ = (('LowPart', wintypes.DWORD),
                ('HighPart', wintypes.LONG))

    def __init__(self, value=0):
        self.HighPart = value >> 32
        self.LowPart = value & ((1 << 32) - 1)

    def __int__(self):
        return self.HighPart << 32 | self.LowPart

PLUID = ctypes.POINTER(LUID)


class LUID_AND_ATTRIBUTES(ctypes.Structure):
    __slots__ = ()
    _fields_ = (('Luid', LUID),
                ('Attributes', wintypes.DWORD))
    def enable(self):
        self.attributes |= SE_PRIVILEGE_ENABLED

PLUID_AND_ATTRIBUTES = ctypes.POINTER(LUID_AND_ATTRIBUTES)


class TOKEN_PRIVILEGES(ctypes.Structure):
    __slots__ = ()
    _fields_ = (('PrivilegeCount', wintypes.DWORD),
                ('_Privileges', LUID_AND_ATTRIBUTES * 1))

    def __init__(self, PrivilegeCount=1):
        if PrivilegeCount < 1:
            raise ValueError('PrivilegeCount must be greater than 0')
        self.PrivilegeCount = PrivilegeCount
        if PrivilegeCount > 1:
            ctypes.resize(self, ctypes.sizeof(self) +
                ctypes.sizeof(LUID_AND_ATTRIBUTES) * (PrivilegeCount - 1))

    @property
    def Privileges(self):
        dt = LUID_AND_ATTRIBUTES * self.PrivilegeCount
        return ctypes.POINTER(dt)(self._Privileges)[0]

PTOKEN_PRIVILEGES = ctypes.POINTER(TOKEN_PRIVILEGES)

advapi32.AdjustTokenPrivileges.restype = wintypes.BOOL
advapi32.AdjustTokenPrivileges.argtypes = (
    wintypes.HANDLE,    # TokenHandle
    wintypes.BOOL,      # DisableAllPrivileges
    PTOKEN_PRIVILEGES,  # NewState
    wintypes.DWORD,     # BufferLength
    PTOKEN_PRIVILEGES,  # PreviousState
    wintypes.LPDWORD)   # ReturnLength

advapi32.LookupPrivilegeValueW.restype = wintypes.BOOL
advapi32.LookupPrivilegeValueW.argtypes = (
    wintypes.LPWSTR,        # lpSystemName
    wintypes.LPWSTR,        # lpName
    ctypes.POINTER(LUID))   # lpLuid

advapi32.OpenProcessToken.restype = wintypes.BOOL
advapi32.OpenProcessToken.argtypes = (
    wintypes.HANDLE,    # ProcessHandle
    wintypes.DWORD,     # DesiredAccess
    wintypes.LPHANDLE)  # TokenHandle

kernel32.CloseHandle.restype = wintypes.BOOL
kernel32.CloseHandle.argtypes = (wintypes.HANDLE,)

kernel32.GetCurrentProcess.restype = wintypes.HANDLE
kernel32.GetCurrentProcess.argtypes = ()


def open_current_process_token(access=TOKEN_ADJUST_PRIVILEGES | TOKEN_QUERY):
    """Retrun a handle for the token of the current process."""
    token = wintypes.HANDLE()
    if not advapi32.OpenProcessToken(
                kernel32.GetCurrentProcess(), access, token):
        raise ctypes.WinError(ctypes.get_last_error())
    return token


def get_privilege_luid(privilege):
    luid = LUID()
    if not advapi32.LookupPrivilegeValueW(
                None, privilege, ctypes.byref(luid)):
        raise ctypes.WinError(ctypes.get_last_error())
    return luid


def adjust_privileges(new_state):
    """Adjust privileges by value (e.g. 18) or name (e.g. SE_RESTORE_NAME).

    new_state is a sequence of 2-tuples: (luid-name, attributes). A
    privilege will be removed if attributes is SE_PRIVILEGE_REMOVED,
    enabled if attributes is SE_PRIVILEGE_ENABLED, and disabled if
    attributes is neither value.

    Returns a 2-tuple: (prev_state, all_assigned). prev_state can be
    passed to this function to restore the previous privilege state of
    the current process token, except for removed privileges.
    all_assigned is true if all of the privileges in new_state were
    assigned to the current process token.
    """
    tp_new_state = TOKEN_PRIVILEGES(len(new_state))
    for (luid, attr), priv in zip(new_state, tp_new_state.Privileges):
        if isinstance(luid, str):
            luid = get_privilege_luid(luid)
        elif isinstance(luid, int):
            luid = LUID(luid)
        priv.Luid = luid
        priv.Attributes = attr

    tp_prev_state = TOKEN_PRIVILEGES(len(new_state))
    rlength = wintypes.DWORD()

    token = open_current_process_token()
    try:
        result = advapi32.AdjustTokenPrivileges(
                    token, False, ctypes.byref(tp_new_state),
                    ctypes.sizeof(tp_new_state), tp_prev_state,
                    ctypes.byref(rlength))
        error = ctypes.get_last_error()
        if not result:
            raise ctypes.WinError(error)
    finally:
        kernel32.CloseHandle(token)

    all_assigned = (error != ERROR_NOT_ALL_ASSIGNED)

    prev_state = []
    for p in tp_prev_state.Privileges[:tp_prev_state.PrivilegeCount]:
        prev_state.append((int(p.Luid), p.Attributes))

    return prev_state, all_assigned


def enable_privilege(privilege):
    new_state = [(privilege, SE_PRIVILEGE_ENABLED)]
    prev_state, all_assigned = adjust_privileges(new_state)
    if not all_assigned:
        raise ctypes.WinError(ERROR_NOT_ALL_ASSIGNED)
    return prev_state


def disable_privilege(privilege):
    new_state = [(privilege, 0)]
    prev_state, all_assigned = adjust_privileges(new_state)
    if not all_assigned:
        raise ctypes.WinError(ERROR_NOT_ALL_ASSIGNED)
    return prev_state


@contextlib.contextmanager
def acquire_privilege(privilege):
    """Try to acquire the given privilege for the current process."""
    prev_state = enable_privilege(privilege)
    try:
        yield
    finally:
        adjust_privileges(prev_state)


def skip_unless_privilege(privilege, restore_early=True):
    """Skip a unit test if the given privilege can't be acquired."""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):

            try:
                prev_state = enable_privilege(privilege)
            except OSError as e:
                if e.winerror == ERROR_NOT_ALL_ASSIGNED:
                    raise unittest.SkipTest(
                        'Privilege "{}" is not available in the '
                        'current process token.'.format(privilege))
                raise

            if restore_early:
                adjust_privileges(prev_state)
            try:
                return func(*args, **kw)
            finally:
                if not restore_early:
                    adjust_privileges(prev_state)
        return wrapper
    return decorator
