import ctypes
import os

class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
    _fields_ = [
        ("cb", ctypes.c_uint32),
        ("PageFaultCount", ctypes.c_uint32),
        ("PeakWorkingSetSize", ctypes.c_size_t),
        ("WorkingSetSize", ctypes.c_size_t),
        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
        ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
        ("PagefileUsage", ctypes.c_size_t),
        ("PeakPagefileUsage", ctypes.c_size_t),
    ]

def debug_mem():
    print(f"OS: {os.name}")
    if os.name == 'nt':
        try:
            pid = os.getpid()
            print(f"PID: {pid}")
            PROCESS_QUERY_INFORMATION = 0x0400
            PROCESS_VM_READ = 0x0010
            handle = ctypes.windll.kernel32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, pid)
            print(f"Handle: {handle}")
            
            if not handle:
                print("Failed to get process handle")
                return 0

            counters = PROCESS_MEMORY_COUNTERS()
            counters.cb = ctypes.sizeof(PROCESS_MEMORY_COUNTERS)
            
            success = ctypes.windll.psapi.GetProcessMemoryInfo(handle, ctypes.byref(counters), counters.cb)
            print(f"PSAPI success: {success}")
            if success:
                print(f"WorkingSetSize: {counters.WorkingSetSize}")
                ctypes.windll.kernel32.CloseHandle(handle)
                return counters.WorkingSetSize
            
            ctypes.windll.kernel32.CloseHandle(handle)
        except Exception as e:
            print(f"Error: {e}")
    return 0

if __name__ == "__main__":
    debug_mem()
