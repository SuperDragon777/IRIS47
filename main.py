import sys
import os
import platform
import getpass
import subprocess
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QTabWidget, 
                             QWidget, QVBoxLayout, QGridLayout, QLineEdit, QPushButton)
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
            domain = subprocess.check_output("wmic computersystem get domain", shell=True).decode().split('\n')[1].strip()
        elif platform.system() == "Linux":
            try:
                with open('/sys/class/dmi/id/sys_vendor', 'r') as f:
                    manufacturer = f.read().strip()
                with open('/sys/class/dmi/id/product_name', 'r') as f:
                    product = f.read().strip()
                domain = "N/A"
            except:
                manufacturer = "N/A"
                product = "N/A"
                domain = "N/A"
        elif platform.system() == "Darwin":
            manufacturer = "Apple Inc."
            try:
                product = subprocess.check_output("sysctl -n hw.model", shell=True).decode().strip()
            except:
                product = "N/A"
            domain = "N/A"
        else:
            manufacturer = "N/A"
            product = "N/A"
            domain = "N/A"
    except:
        manufacturer = "N/A"
        product = "N/A"
        domain = "N/A"
    
    return manufacturer, product, domain

def get_os_info():
    os_name = platform.system()
    os_version = platform.version()
    os_release = platform.release()
    return f"{os_name} {os_release} ({os_version})"

def get_gpu_info():
    gpus = []
    try:
        if platform.system() == "Windows":
            import wmi
            try:
                c = wmi.WMI()
                for gpu in c.Win32_VideoController():
                    name = gpu.Name
                    try:
                        ram_gb = int(gpu.AdapterRAM) / (1024**3)
                        gpus.append(f"{name} ({ram_gb:.0f} GB)")
                    except:
                        gpus.append(name)
            except:
                result = subprocess.check_output("wmic path win32_VideoController get name", shell=True).decode()
                lines = [line.strip() for line in result.split('\n') if line.strip() and 'Name' not in line]
                gpus = lines if lines else ["N/A"]
        elif platform.system() == "Linux":
            try:
                result = subprocess.check_output("lspci | grep -i vga", shell=True).decode()
                lines = result.strip().split('\n')
                for line in lines:
                    gpu = line.split(': ')[-1]
                    gpus.append(gpu)
            except:
                gpus = ["N/A"]
        elif platform.system() == "Darwin":
            try:
                result = subprocess.check_output("system_profiler SPDisplaysDataType | grep Chipset", shell=True).decode()
                lines = result.strip().split('\n')
                for line in lines:
                    gpu = line.split(': ')[-1].strip()
                    gpus.append(gpu)
            except:
                gpus = ["N/A"]
    except:
        gpus = ["N/A"]
    
    return gpus if gpus else ["N/A"]

def get_monitors_info():
    monitors = []
    try:
        if platform.system() == "Windows":
            import wmi
            try:
                c = wmi.WMI(namespace='wmi')
                for monitor in c.WmiMonitorID():
                    try:
                        name = ''.join([chr(x) for x in monitor.UserFriendlyName if x != 0])
                        serial = ''.join([chr(x) for x in monitor.SerialNumberID if x != 0])
                        year = monitor.YearOfManufacture
                        
                        monitor_str = f"{name}"
                        if serial:
                            monitor_str += f" ({serial})"
                        if year:
                            monitor_str += f" [{year}]"
                        
                        monitors.append(monitor_str)
                    except:
                        continue
            except:
                pass
            
            if not monitors:
                try:
                    result = subprocess.check_output('powershell "Get-WmiObject WmiMonitorID -Namespace root\\wmi | Select-Object UserFriendlyName"', shell=True).decode()
                    monitors = ["Monitor detected"]
                except:
                    monitors = ["N/A"]
                    
        elif platform.system() == "Linux":
            try:
                result = subprocess.check_output("xrandr --query | grep ' connected'", shell=True).decode()
                lines = result.strip().split('\n')
                for line in lines:
                    monitor = line.split()[0]
                    monitors.append(monitor)
            except:
                monitors = ["N/A"]
        elif platform.system() == "Darwin":
            try:
                result = subprocess.check_output("system_profiler SPDisplaysDataType | grep Resolution", shell=True).decode()
                lines = result.strip().split('\n')
                for i, line in enumerate(lines):
                    monitors.append(f"Display {i+1}")
            except:
                monitors = ["N/A"]
    except:
        monitors = ["N/A"]
    
    return monitors if monitors else ["N/A"]

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IRIS47")
        self.setFixedSize(900, 700)
        
        icon_path = resource_path('icon.png')
        self.setWindowIcon(QIcon(icon_path))
        
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.refresh_data)
        main_layout.addWidget(refresh_button)
        
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
        self.init_system_tab()
        self.init_display_tab()
    
    def refresh_data(self):
        self.tabs.clear()
        self.init_system_tab()
        self.init_display_tab()
    
    def init_system_tab(self):
        system_tab = QWidget()
        layout = QGridLayout()
        
        computer_name = platform.node()
        user_name = getpass.getuser()
        manufacturer, product, domain = get_system_info()
        os_info = get_os_info()
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        layout.addWidget(QLabel("Computer Name:"), 0, 0)
        layout.addWidget(self.create_readonly_field(computer_name), 0, 1)
        
        layout.addWidget(QLabel("User Name:"), 1, 0)
        layout.addWidget(self.create_readonly_field(user_name), 1, 1)
        
        layout.addWidget(QLabel("Manufacturer:"), 2, 0)
        layout.addWidget(self.create_readonly_field(manufacturer), 2, 1)
        
        layout.addWidget(QLabel("Product Name:"), 3, 0)
        layout.addWidget(self.create_readonly_field(product), 3, 1)
        
        layout.addWidget(QLabel("Operating System:"), 4, 0)
        layout.addWidget(self.create_readonly_field(os_info), 4, 1)
        
        layout.addWidget(QLabel("Domain:"), 5, 0)
        layout.addWidget(self.create_readonly_field(domain), 5, 1)
        
        layout.addWidget(QLabel("Date and Time:"), 6, 0)
        layout.addWidget(self.create_readonly_field(current_datetime), 6, 1)
        
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        system_tab.setLayout(layout)
        
        self.tabs.addTab(system_tab, "System")
    
    def init_display_tab(self):
        display_tab = QWidget()
        layout = QGridLayout()
        
        gpus = get_gpu_info()
        monitors = get_monitors_info()
        
        row = 0
        for i, gpu in enumerate(gpus):
            label = "Video Adapter:" if i == 0 else ""
            layout.addWidget(QLabel(label), row, 0)
            layout.addWidget(self.create_readonly_field(gpu), row, 1)
            row += 1
        
        for i, monitor in enumerate(monitors):
            label = "Monitor:" if i == 0 else ""
            layout.addWidget(QLabel(label), row, 0)
            layout.addWidget(self.create_readonly_field(monitor), row, 1)
            row += 1
        
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        display_tab.setLayout(layout)
        
        self.tabs.addTab(display_tab, "Display")
    
    def create_readonly_field(self, text):
        field = QLineEdit(text)
        field.setReadOnly(True)
        field.setCursor(Qt.CursorShape.IBeamCursor)
        return field

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    icon_path = resource_path('icon.png')
    app.setWindowIcon(QIcon(icon_path))
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())