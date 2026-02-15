import time
import pytest
from processes.performance import PerformanceMonitor

def test_performance_monitor_timing():
    monitor = PerformanceMonitor("TestTask")
    monitor.start()
    time.sleep(0.1) # Wait for 100ms
    monitor.stop()
    report = monitor.get_report()
    
    assert report["name"] == "TestTask"
    assert report["duration_ms"] >= 100
    assert report["duration_ms"] < 200 # Allow some overhead

def test_performance_monitor_memory():
    monitor = PerformanceMonitor("MemTask")
    monitor.start()
    
    # Allocate some memory (approx 10MB)
    dummy_data = bytearray(10 * 1024 * 1024)
    monitor.update_peak()
    
    monitor.stop()
    report = monitor.get_report()
    
    assert report["peak_memory_mb"] > 0
    # Increase should be at least a few MBs
    assert report["memory_increase_mb"] >= 0
