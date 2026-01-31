import sys
import os
import platform
import getpass
import subprocess
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QTabWidget, 
                             QWidget, QVBoxLayout, QGridLayout)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

def get_system_info():
    try:
        if platform.system() == "Windows":
            manufacturer = subprocess.check_output("wmic computersystem get manufacturer", shell=True).decode().split('\n')[1].strip()
            product = subprocess.check_output("wmic computersystem get model", shell=True).decode().split('\n')[1].strip()
        else:
            manufacturer = "N/A"
            product = "N/A"
    except:
        manufacturer = "N/A"
        product = "N/A"
    
    return manufacturer, product

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IRIS47")
        self.setFixedSize(900, 700)
        
        icon_path = resource_path('icon.png')
        self.setWindowIcon(QIcon(icon_path))
        
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        self.init_system_tab()
    
    def init_system_tab(self):
        system_tab = QWidget()
        layout = QGridLayout()
        
        computer_name = platform.node()
        user_name = getpass.getuser()
        manufacturer, product = get_system_info()
        
        layout.addWidget(QLabel("Computer Name:"), 0, 0)
        layout.addWidget(QLabel(computer_name), 0, 1)
        
        layout.addWidget(QLabel("User Name:"), 1, 0)
        layout.addWidget(QLabel(user_name), 1, 1)
        
        layout.addWidget(QLabel("Manufacturer:"), 2, 0)
        layout.addWidget(QLabel(manufacturer), 2, 1)
        
        layout.addWidget(QLabel("Product Name:"), 3, 0)
        layout.addWidget(QLabel(product), 3, 1)
        
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        system_tab.setLayout(layout)
        
        self.tabs.addTab(system_tab, "System")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    icon_path = resource_path('icon.png')
    app.setWindowIcon(QIcon(icon_path))
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())