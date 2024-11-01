import ctypes
import win32security

def enable_se_impersonate_privilege():
    try:
        # الحصول على معلومات المستخدم الحالي
        user_token = win32security.OpenProcessToken(ctypes.windll.kernel32.GetCurrentProcess(), win32security.TOKEN_ALL_ACCESS)

        # الحصول على معلومات الامتيازات
        privileges = win32security.GetTokenInformation(user_token, win32security.TokenPrivileges)

        # البحث عن الامتياز SeImpersonatePrivilege
        for privilege in privileges:
            if privilege[0] == win32security.LookupPrivilegeValue(None, "SeImpersonatePrivilege"):
                # تم العثور على الامتياز، نقوم بتمكينه
                win32security.AdjustTokenPrivileges(user_token, 0, [(privilege[0], win32security.SE_PRIVILEGE_ENABLED)])

                print("SeImpersonatePrivilege enabled")
                return

        print("SeImpersonatePrivilege not found")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    enable_se_impersonate_privilege()
