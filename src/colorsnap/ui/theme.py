STYLESHEET = """
QWidget{background:#181820;color:#ECECF1;font-family:'Segoe UI',Arial,sans-serif;font-size:13px}
QMainWindow,QDialog{background:#181820}
QFrame#sidebar{background:#12121A;border-right:1px solid #2A2A3A}
QFrame#panel, QFrame#card{background:#21212E;border:1px solid #2E2E42;border-radius:12px}
QPushButton{background:#2C2C40;border:1px solid #3A3A55;border-radius:8px;padding:8px 14px;color:#ECECF1}
QPushButton:hover{background:#3A3555;border-color:#8B5CF6}
QPushButton:pressed{background:#4C1D95}
QPushButton#primary{background:#7C3AED;border-color:#8B5CF6;font-weight:600}
QPushButton#primary:hover{background:#8B5CF6}
QPushButton#nav{background:transparent;border:none;text-align:left;padding:10px 14px;border-radius:8px}
QPushButton#nav:hover{background:#23233A}
QPushButton#nav:checked{background:#2E1065;border:1px solid #7C3AED}
QLineEdit,QSpinBox,QComboBox{background:#12121A;border:1px solid #3A3A55;border-radius:8px;padding:7px}
QLineEdit:focus,QSpinBox:focus{border-color:#8B5CF6}
QLabel#title{font-size:22px;font-weight:700} QLabel#subtitle{color:#A0A0B5} QLabel#muted{color:#A0A0B5}
QListWidget{background:#12121A;border:1px solid #2E2E42;border-radius:10px}
QStatusBar{background:#12121A;color:#A0A0B5}
QToolTip{background:#2C2C40;color:#fff;border:1px solid #8B5CF6}
QScrollArea{border:none}
"""
LIGHT_STYLESHEET = STYLESHEET.replace("#181820","#F4F4F8").replace("#ECECF1","#1B1B26").replace("#12121A","#FFFFFF").replace("#21212E","#FFFFFF").replace("#2C2C40","#E8E8F2")
