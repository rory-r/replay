import sys
import header
from ui import *
from other import *

import time

def main():
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
    
if __name__ == '__main__':
    main()
