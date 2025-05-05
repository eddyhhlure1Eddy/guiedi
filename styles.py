# 自定义样式表模块

# 暗黑主题样式表
DARK_STYLESHEET = """
QMainWindow, QDialog, QWidget {
    background-color: #1e1e1e;
    color: #e0e0e0;
}

QMenuBar, QMenu {
    background-color: #252525;
    color: #e0e0e0;
    border: 1px solid #373737;
}

QMenuBar::item:selected, QMenu::item:selected {
    background-color: #3a3a3a;
}

QToolBar {
    background-color: #2d2d2d;
    border: 1px solid #373737;
    spacing: 3px;
}

QToolButton {
    background-color: #2d2d2d;
    border: 1px solid #373737;
    border-radius: 3px;
}

QToolButton:hover {
    background-color: #3a3a3a;
    border: 1px solid #5e5e5e;
}

QToolButton:pressed {
    background-color: #3a3a3a;
}

QPushButton {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 1px solid #373737;
    border-radius: 3px;
    padding: 5px;
    min-width: 80px;
}

QPushButton:hover {
    background-color: #3a3a3a;
    border: 1px solid #5e5e5e;
}

QPushButton:pressed {
    background-color: #444444;
}

QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox {
    background-color: #252525;
    color: #e0e0e0;
    border: 1px solid #373737;
    border-radius: 3px;
    padding: 2px;
}

QComboBox {
    background-color: #252525;
    color: #e0e0e0;
    border: 1px solid #373737;
    border-radius: 3px;
    padding: 1px 18px 1px 3px;
    min-width: 6em;
}

QComboBox:hover {
    border: 1px solid #5e5e5e;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 15px;
    border-left: 1px solid #373737;
}

QComboBox QAbstractItemView {
    background-color: #252525;
    color: #e0e0e0;
    border: 1px solid #373737;
    selection-background-color: #3a3a3a;
}

QLabel {
    color: #e0e0e0;
}

QTabWidget::pane {
    border: 1px solid #373737;
}

QTabBar::tab {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 1px solid #373737;
    border-bottom-color: #373737;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    min-width: 8ex;
    padding: 2px 8px;
    margin-right: 2px;
}

QTabBar::tab:selected, QTabBar::tab:hover {
    background-color: #3a3a3a;
}

QTabBar::tab:selected {
    border-bottom-color: #3a3a3a;
}

QDockWidget {
    border: 1px solid #373737;
    titlebar-close-icon: url(close.png);
    titlebar-normal-icon: url(normal.png);
}

QDockWidget::title {
    text-align: left;
    background-color: #2d2d2d;
    padding-left: 5px;
}

QListWidget, QTreeWidget, QTableWidget {
    background-color: #252525;
    color: #e0e0e0;
    border: 1px solid #373737;
    alternate-background-color: #2a2a2a;
}

QListWidget::item:selected, QTreeWidget::item:selected, QTableWidget::item:selected {
    background-color: #3a3a3a;
    color: #e0e0e0;
}

QScrollBar:vertical {
    background-color: #2d2d2d;
    width: 12px;
    margin: 12px 0 12px 0;
    border: 1px solid #373737;
    border-radius: 2px;
}

QScrollBar::handle:vertical {
    background-color: #5e5e5e;
    min-height: 20px;
    border-radius: 2px;
}

QScrollBar::add-line:vertical {
    border: none;
    background: none;
    height: 10px;
    subcontrol-position: bottom;
    subcontrol-origin: margin;
}

QScrollBar::sub-line:vertical {
    border: none;
    background: none;
    height: 10px;
    subcontrol-position: top;
    subcontrol-origin: margin;
}

QScrollBar:horizontal {
    background-color: #2d2d2d;
    height: 12px;
    margin: 0 12px 0 12px;
    border: 1px solid #373737;
    border-radius: 2px;
}

QScrollBar::handle:horizontal {
    background-color: #5e5e5e;
    min-width: 20px;
    border-radius: 2px;
}

QScrollBar::add-line:horizontal {
    border: none;
    background: none;
    width: 10px;
    subcontrol-position: right;
    subcontrol-origin: margin;
}

QScrollBar::sub-line:horizontal {
    border: none;
    background: none;
    width: 10px;
    subcontrol-position: left;
    subcontrol-origin: margin;
}

QSlider::groove:horizontal {
    border: 1px solid #373737;
    height: 4px;
    background: #3a3a3a;
    margin: 0px;
    border-radius: 2px;
}

QSlider::handle:horizontal {
    background: #007acc;
    border: 1px solid #373737;
    width: 12px;
    height: 12px;
    margin: -4px 0;
    border-radius: 6px;
}

QSlider::handle:horizontal:hover {
    background: #009aee;
}

QGroupBox {
    border: 1px solid #373737;
    border-radius: 3px;
    margin-top: 1ex;
    font-weight: bold;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 3px;
    color: #e0e0e0;
}

QHeaderView::section {
    background-color: #2d2d2d;
    color: #e0e0e0;
    padding: 4px;
    border: 1px solid #373737;
    border-top: 1px solid #373737;
}

QSizeGrip {
    width: 16px;
    height: 16px;
}

QToolTip {
    border: 1px solid #373737;
    background-color: #252525;
    color: #e0e0e0;
    padding: 2px;
    opacity: 200;
}
"""

# 现代积木风格样式表 - 浅色主题
BLOCKS_LIGHT_STYLESHEET = """
QMainWindow, QDialog, QWidget {
    background-color: #f0f0f0;
    color: #333333;
}

QMenuBar, QMenu {
    background-color: #ffffff;
    color: #333333;
    border: 1px solid #dddddd;
}

QMenuBar::item:selected, QMenu::item:selected {
    background-color: #e6e6e6;
}

QToolBar {
    background-color: #ffffff;
    border: 1px solid #dddddd;
    spacing: 3px;
}

QToolButton {
    background-color: #ffffff;
    border: 1px solid #dddddd;
    border-radius: 5px;
    padding: 4px;
}

QToolButton:hover {
    background-color: #e6e6e6;
    border: 1px solid #bbbbbb;
}

QToolButton:pressed {
    background-color: #d9d9d9;
}

QPushButton {
    background-color: #4d94ff;
    color: white;
    border: none;
    border-radius: 5px;
    padding: 8px 16px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #3a85ff;
}

QPushButton:pressed {
    background-color: #2a75ff;
}

QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox {
    background-color: white;
    color: #333333;
    border: 2px solid #dddddd;
    border-radius: 5px;
    padding: 6px;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {
    border: 2px solid #4d94ff;
}

QComboBox {
    background-color: white;
    color: #333333;
    border: 2px solid #dddddd;
    border-radius: 5px;
    padding: 6px 12px 6px 6px;
    min-width: 6em;
}

QComboBox:hover {
    border: 2px solid #bbbbbb;
}

QComboBox:focus {
    border: 2px solid #4d94ff;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 15px;
    border-left: 1px solid #dddddd;
}

QComboBox QAbstractItemView {
    background-color: white;
    color: #333333;
    border: 1px solid #dddddd;
    selection-background-color: #e6e6e6;
}

QLabel {
    color: #333333;
    font-size: 13px;
}

QGroupBox {
    border: 2px solid #dddddd;
    border-radius: 5px;
    margin-top: 1ex;
    font-weight: bold;
    background-color: rgba(255, 255, 255, 150);
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 5px;
    color: #333333;
    background-color: #f0f0f0;
}

/* 积木风格特别样式 */
#widget_container QWidget {
    margin: 2px;
}

#widget_box QListWidget::item {
    background-color: white;
    border: 2px solid #dddddd;
    border-radius: 5px;
    margin: 5px;
    padding: 10px;
}

#widget_box QListWidget::item:hover {
    background-color: #e6e6e6;
    border-color: #bbbbbb;
}

#widget_box QListWidget::item:selected {
    background-color: #d9d9d9;
    border-color: #4d94ff;
}

#design_canvas QWidget {
    margin: 2px;
    border: 2px solid transparent;
}

#design_canvas QWidget:hover {
    border: 2px dashed #bbbbbb;
}

#design_canvas QWidget[selected="true"] {
    border: 2px solid #4d94ff !important;
}
"""
