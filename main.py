import sys
import os
import platform
import getpass
import subprocess
import shutil
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
        import GPUtil
        gpu_list = GPUtil.getGPUs()
        for gpu in gpu_list:
            gpus.append(f"{gpu.name} ({gpu.memoryTotal:.0f} MB)")
    except:
        pass
    
    if not gpus:
        try:
            if platform.system() == "Windows":
                result = subprocess.check_output("wmic path win32_VideoController get name", shell=True).decode()
                lines = [line.strip() for line in result.split('\n') if line.strip() and 'Name' not in line]
                gpus = lines if lines else ["N/A"]
                
            elif platform.system() == "Linux":
                try:
                    result = subprocess.check_output(
                        "nvidia-smi --query-gpu=name,memory.total --format=csv,noheader", 
                        shell=True
                    ).decode()
                    lines = result.strip().split('\n')
                    for line in lines:
                        gpus.append(line.strip())
                except:
                    result = subprocess.check_output("lspci | grep -i vga", shell=True).decode()
                    lines = result.strip().split('\n')
                    for line in lines:
                        gpu = line.split(': ')[-1]
                        gpus.append(gpu)
                        
            elif platform.system() == "Darwin":
                try:
                    result = subprocess.check_output(
                        "system_profiler SPDisplaysDataType | grep 'Chipset Model\\|VRAM'", 
                        shell=True
                    ).decode()
                    lines = result.strip().split('\n')
                    current_gpu = None
                    for line in lines:
                        if 'Chipset Model' in line:
                            current_gpu = line.split(': ')[-1].strip()
                        elif 'VRAM' in line and current_gpu:
                            vram = line.split(': ')[-1].strip()
                            gpus.append(f"{current_gpu} ({vram})")
                            current_gpu = None
                    if current_gpu:
                        gpus.append(current_gpu)
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

def get_disk_info():
    disks = []
    try:
        if platform.system() == "Windows":
            result = subprocess.check_output("wmic diskdrive get Model,Size,SerialNumber", shell=True).decode()
            lines = [line.strip() for line in result.split('\n')[1:] if line.strip()]
            for line in lines:
                parts = line.split()
                if len(parts) >= 2:
                    size_bytes = parts[-1] if parts[-1].isdigit() else "0"
                    size_gb = int(size_bytes) / (1024**3) if size_bytes.isdigit() else 0
                    model = ' '.join(parts[:-2]) if len(parts) > 2 else ' '.join(parts[:-1])
                    serial = parts[-2] if len(parts) > 2 and not parts[-2].isdigit() else ""
                    
                    disk_str = f"{model} ({size_gb:.0f} GB)"
                    if serial and not serial.isdigit():
                        disk_str += f" [{serial}]"
                    disks.append(disk_str)
                    
        elif platform.system() == "Linux":
            result = subprocess.check_output("lsblk -d -o NAME,SIZE,MODEL -n", shell=True).decode()
            lines = result.strip().split('\n')
            for line in lines:
                parts = line.split(None, 2)
                if len(parts) >= 2 and not parts[0].startswith('loop'):
                    name = parts[0]
                    size = parts[1]
                    model = parts[2] if len(parts) > 2 else "Unknown"
                    disks.append(f"{model} ({size})")
                    
        elif platform.system() == "Darwin":
            result = subprocess.check_output("diskutil list", shell=True).decode()
            lines = result.split('\n')
            for line in lines:
                if '/dev/disk' in line and 'synthesized' not in line.lower():
                    parts = line.split()
                    if len(parts) >= 3:
                        size = parts[3] + parts[4] if len(parts) > 4 else parts[3]
                        name = ' '.join(parts[5:]) if len(parts) > 5 else "Disk"
                        disks.append(f"{name} ({size})")
    except:
        disks = ["N/A"]
    
    return disks if disks else ["N/A"]

def get_partitions_info():
    partitions = []
    total_size = 0
    total_free = 0
    
    try:
        if platform.system() == "Windows":
            import string
            for letter in string.ascii_uppercase:
                drive = f"{letter}:\\"
                if os.path.exists(drive):
                    try:
                        usage = shutil.disk_usage(drive)
                        total_gb = usage.total / (1024**3)
                        free_gb = usage.free / (1024**3)
                        
                        fs_type = "NTFS"
                        try:
                            result = subprocess.check_output(f'wmic logicaldisk where "DeviceID=\'{letter}:\'" get FileSystem', shell=True).decode()
                            lines = [line.strip() for line in result.split('\n') if line.strip() and 'FileSystem' not in line]
                            if lines:
                                fs_type = lines[0]
                        except:
                            pass
                        
                        partitions.append(f"{letter}: ({fs_type}) {total_gb:.1f} GB ({free_gb:.1f} GB free)")
                        total_size += total_gb
                        total_free += free_gb
                    except:
                        pass
                        
        elif platform.system() == "Linux":
            result = subprocess.check_output("df -h -T -x tmpfs -x devtmpfs", shell=True).decode()
            lines = result.strip().split('\n')[1:]
            for line in lines:
                parts = line.split()
                if len(parts) >= 7 and parts[0].startswith('/dev/'):
                    device = parts[0]
                    fs_type = parts[1]
                    size = parts[2]
                    avail = parts[4]
                    mount = parts[6]
                    
                    partitions.append(f"{mount} ({fs_type}) {size} ({avail} free)")
                    
                    try:
                        usage = shutil.disk_usage(mount)
                        total_size += usage.total / (1024**3)
                        total_free += usage.free / (1024**3)
                    except:
                        pass
                        
        elif platform.system() == "Darwin":
            result = subprocess.check_output("df -h", shell=True).decode()
            lines = result.strip().split('\n')[1:]
            for line in lines:
                parts = line.split()
                if len(parts) >= 9 and parts[0].startswith('/dev/disk'):
                    device = parts[0]
                    size = parts[1]
                    avail = parts[3]
                    mount = ' '.join(parts[8:])
                    
                    partitions.append(f"{mount} {size} ({avail} free)")
                    
                    try:
                        usage = shutil.disk_usage(mount)
                        total_size += usage.total / (1024**3)
                        total_free += usage.free / (1024**3)
                    except:
                        pass
    except:
        partitions = ["N/A"]
    
    return partitions, total_size, total_free

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
        self.init_disk_tab()
    
    def refresh_data(self):
        self.tabs.clear()
        self.init_system_tab()
        self.init_display_tab()
        self.init_disk_tab()
    
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
    
    def init_disk_tab(self):
        disk_tab = QWidget()
        layout = QGridLayout()
        
        disks = get_disk_info()
        partitions, total_size, total_free = get_partitions_info()
        
        row = 0
        for i, disk in enumerate(disks):
            label = "Disk:" if i == 0 else ""
            layout.addWidget(QLabel(label), row, 0)
            layout.addWidget(self.create_readonly_field(disk), row, 1)
            row += 1
        
        layout.addWidget(QLabel(""), row, 0)
        row += 1
        
        layout.addWidget(QLabel("Partitions:"), row, 0)
        row += 1
        
        for i, partition in enumerate(partitions):
            layout.addWidget(QLabel(""), row, 0)
            layout.addWidget(self.create_readonly_field(partition), row, 1)
            row += 1
        
        if total_size > 0:
            layout.addWidget(QLabel(""), row, 0)
            row += 1
            layout.addWidget(QLabel("Total Size:"), row, 0)
            layout.addWidget(self.create_readonly_field(f"{total_size:.1f} GB ({total_free:.1f} GB free)"), row, 1)
        
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        disk_tab.setLayout(layout)
        
        self.tabs.addTab(disk_tab, "Disk")
    
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