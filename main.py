import multiprocessing

# Must run before anything else in the packaged app. Some libraries (py-cpuinfo on the diagnostics page)
# start helper processes by re-running this program; without this each helper would open another full
# copy of the app, and so on.
multiprocessing.freeze_support()

import sys
import time
from PyQt6.QtWidgets import QApplication
from src.main_window import MainWindow
from src.splash_screen import RideShieldSplash

def main():
    app = QApplication(sys.argv)
    from src import theme
    theme.load_fonts()
    app.setApplicationName("RideShield AI")

    splash = RideShieldSplash()
    splash.show()
    app.processEvents()
    
    splash.set_progress(10, "Loading UI Assets...")
    time.sleep(0.4)
    app.processEvents()
    
    splash.set_progress(40, "Loading AI model...")
    time.sleep(0.8)
    app.processEvents()
    
    splash.set_progress(70, "Connecting to Camera Stream...")
    time.sleep(0.6)
    app.processEvents()
    
    splash.set_progress(90, "Initializing Analytics Engine...")
    time.sleep(0.4)
    app.processEvents()
    
    # Initialize main window (which starts the camera)
    window = MainWindow()
    
    splash.set_progress(100, "System Ready.")
    time.sleep(0.2)
    app.processEvents()
    
    window.show()
    splash.finish(window)
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
