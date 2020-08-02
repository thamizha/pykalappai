__author__ = "Manikk, Vijay, Mohanrex"
__copyright__ = "Copyright (c) 2015 http://thamizha.com/"
__credits__ = ["Manikk, Vijay, Mohan"]
__license__ = "GNU/GPL v3 or (at your option) any later version."
__version__ = "4.0.0"
__maintainer__ = "http://thamizha.com/"
__email__ = ""
__status__ = "Development"

# Entry file which will bootstrap the app and start the application

import time
import sys

from PyQt5.QtWidgets import QApplication
from PyQt5.Qt import QSharedMemory, QSplashScreen
from PyQt5.QtCore import qWarning
from PyQt5.QtGui import QPixmap

from resources import ekalappai_rc
from Controllers import EKWindow


class Main:

    def __init__(self):
        # Initialize
        app = QApplication(sys.argv)
        app.setApplicationName("eKalappai")
        app.setApplicationVersion("4.0.0")
        shared = QSharedMemory("59698760-43bb-44d9-8121-181ecbb70e4d")

        # Check if already another instance of app is running and quit if it is
        if not shared.create(512, QSharedMemory.ReadWrite):
            qWarning("Cannot start more than one instance of eKalappai any time.")
            exit(0)

        # Splash Screen init
        splashImage = QPixmap(':intro/splash_screen')
        splashScreen = QSplashScreen(splashImage)
        splashScreen.show()
        # Time wait for splash screen to be shown
        time.sleep(2)
        splashScreen.hide()

        # Main application starting
        QApplication.setQuitOnLastWindowClosed(False)
        ekWindow = EKWindow(app)

        # EK Engine start
        ekWindow.engine.start()
        
        sys.exit(app.exec_())


if __name__ == "__main__":
    main = Main()
