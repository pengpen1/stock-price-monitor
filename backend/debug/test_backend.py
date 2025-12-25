from monitor import StockMonitor
import time
import threading

def test_monitor():
    monitor = StockMonitor()
    
    # Start monitor in a thread
    t = threading.Thread(target=monitor.start, daemon=True)
    t.start()
    
    print("Adding stock 600519 (Moutai)...")
    monitor.add_stock("600519")
    
    # Wait for a fetch cycle
    time.sleep(10)
    
    data = monitor.get_stocks()
    print("Current Data:", data)
    
    monitor.stop()

if __name__ == "__main__":
    test_monitor()
