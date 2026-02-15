import time
import os
import ctypes
from typing import Dict

# Windows-specific memory tracking
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

def get_current_memory_mb() -> float:
    """Returns current process RSS memory usage in MB."""
    if os.name == 'nt':
        try:
            PROCESS_QUERY_INFORMATION = 0x0400
            PROCESS_VM_READ = 0x0010
            pid = os.getpid()
            handle = ctypes.windll.kernel32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, pid)
            if not handle:
                return 0.0

            counters = PROCESS_MEMORY_COUNTERS()
            counters.cb = ctypes.sizeof(PROCESS_MEMORY_COUNTERS)
            
            success = ctypes.windll.psapi.GetProcessMemoryInfo(handle, ctypes.byref(counters), counters.cb)
            ctypes.windll.kernel32.CloseHandle(handle)
            
            if success:
                return counters.WorkingSetSize / (1024 * 1024)
            return 0.0
        except:
            return 0.0
    else:
        # Fallback for Unix-like systems if needed
        try:
            import resource
            return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0
        except:
            return 0.0

class PerformanceMonitor:
    def __init__(self, name: str):
        self.name = name
        self.start_time = 0
        self.end_time = 0
        self.start_mem = 0
        self.peak_mem = 0
        self.is_running = False

    def start(self):
        self.start_time = time.perf_counter()
        self.start_mem = get_current_memory_mb()
        self.peak_mem = self.start_mem
        self.is_running = True

    def update_peak(self):
        """Should be called periodically to track peak memory."""
        if self.is_running:
            curr_mem = get_current_memory_mb()
            if curr_mem > self.peak_mem:
                self.peak_mem = curr_mem

    def stop(self):
        self.end_time = time.perf_counter()
        self.update_peak()
        self.is_running = False

    def get_report(self) -> Dict:
        duration_ms = (self.end_time - self.start_time) * 1000
        return {
            "name": self.name,
            "duration_ms": duration_ms,
            "peak_memory_mb": self.peak_mem,
            "memory_increase_mb": self.peak_mem - self.start_mem
        }
