__author__ = "Manikk, Vijay, Mohan"
__copyright__ = "Copyright (c) 2015 http://thamizha.com/"
__credits__ = ["Manikk, Vijay, Mohan"]
__license__ = "GNU/GPL v3 or (at your option) any later version."
__version__ = "4.0.0"
__maintainer__ = "http://thamizha.com/"
__email__ = ""
__status__ = "Development"

import time
import sys

from EkEngine import Engine


class Main:

    def __init__(self):
        self.filePath = "tables\Tamil-phonetic.txt.in"
        self.engine = Engine(self.filePath)
        self.engine.start()


if __name__ == "__main__":
    main = Main()

