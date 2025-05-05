import sys
from PyQt5.QtWidgets import (QListWidget, QListWidgetItem, QWidget, QLabel, QPushButton, QVBoxLayout,
                              QLineEdit, QTextEdit, QCheckBox, QRadioButton, QComboBox, QSpinBox,
                              QSlider, QGroupBox, QTabWidget, QTableWidget, QScrollArea, QGridLayout,
                              QSizePolicy, QSpacerItem, QMenu)
from PyQt5.QtCore import Qt, QMimeData, QSize, QRect, QPoint, pyqtSignal, QEvent
from PyQt5.QtGui import QDrag, QPixmap, QPainter, QPen, QColor, QCursor, QLinearGradient, QFont

# 可用的控件类型 - 积木库
WIDGET_TYPES = {
    "QPushButton": {"icon": "🔘", "text": "按钮", "description": "可点击的按钮控件"},
    "QLabel": {"icon": "🏷️", "text": "标签", "description": "显示文本或图像的标签"},
    "QLineEdit": {"icon": "📝", "text": "单行文本框", "description": "输入单行文本的控件"},
    "QTextEdit": {"icon": "📄", "text": "多行文本框", "description": "输入多行文本的控件"},
    "QCheckBox": {"icon": "✅", "text": "复选框", "description": "可选中/取消选中的控件"},
    "QRadioButton": {"icon": "⭕", "text": "单选按钮", "description": "互斥选择的单选按钮"},
    "QComboBox": {"icon": "📋", "text": "下拉框", "description": "下拉选择控件"},
    "QSpinBox": {"icon": "🔢", "text": "数字输入", "description": "输入数值的控件"},
    "QSlider": {"icon": "📊", "text": "滑块", "description": "滑动选择数值的控件"},
    "QGroupBox": {"icon": "📦", "text": "分组框", "description": "对控件进行分组的容器"},
    "QTabWidget": {"icon": "📑", "text": "选项卡", "description": "带标签页切换的容器"},
    "QTableWidget": {"icon": "🗓️", "text": "表格", "description": "表格数据控件"},
    "QListWidget": {"icon": "📜", "text": "列表", "description": "列表数据控件"},
}

# 控件工厂 - 用于创建各种类型的控件
class WidgetFactory:
    @staticmethod
    def create_widget(widget_type, parent=None):
        """创建指定类型的控件"""
        if widget_type == "QPushButton":
            widget = QPushButton("按钮", parent)
            widget.setMinimumSize(80, 30)
            return widget
        
        elif widget_type == "QLabel":
            widget = QLabel("标签", parent)
            widget.setMinimumSize(60, 20)
            return widget
        
        elif widget_type == "QLineEdit":
            widget = QLineEdit(parent)
            widget.setPlaceholderText("请输入文本")
            widget.setMinimumSize(120, 30)
            return widget
        
        elif widget_type == "QTextEdit":
            widget = QTextEdit(parent)
            widget.setPlaceholderText("请输入多行文本")
            widget.setMinimumSize(200, 120)
            return widget
        
        elif widget_type == "QCheckBox":
            widget = QCheckBox("复选框", parent)
            return widget
        
        elif widget_type == "QRadioButton":
            widget = QRadioButton("单选按钮", parent)
            return widget
        
        elif widget_type == "QComboBox":
            widget = QComboBox(parent)
            widget.addItems(["选项1", "选项2", "选项3"])
            widget.setMinimumSize(120, 30)
            return widget
        
        elif widget_type == "QSpinBox":
            widget = QSpinBox(parent)
            widget.setRange(0, 100)
            widget.setValue(50)
            widget.setMinimumSize(80, 30)
            return widget
        
        elif widget_type == "QSlider":
            widget = QSlider(Qt.Horizontal, parent)
            widget.setRange(0, 100)
            widget.setValue(50)
            widget.setMinimumSize(150, 30)
            return widget
        
        elif widget_type == "QGroupBox":
            widget = QGroupBox("分组", parent)
            layout = QVBoxLayout(widget)
            widget.setLayout(layout)
            widget.setMinimumSize(200, 150)
            return widget
        
        elif widget_type == "QTabWidget":
            widget = QTabWidget(parent)
            tab1 = QWidget()
            tab2 = QWidget()
            widget.addTab(tab1, "标签页1")
            widget.addTab(tab2, "标签页2")
            widget.setMinimumSize(250, 180)
            return widget
        
        elif widget_type == "QTableWidget":
            widget = QTableWidget(4, 4, parent)
            for i in range(4):
                for j in range(4):
                    widget.setItem(i, j, QTableWidget.QTableWidgetItem(f"({i},{j})"))
            widget.setMinimumSize(250, 200)
            return widget
        
        elif widget_type == "QListWidget":
            widget = QListWidget(parent)
            widget.addItems(["项目1", "项目2", "项目3", "项目4"])
            widget.setMinimumSize(150, 180)
            return widget
        
        else:
            # 默认创建一个占位控件
            widget = QLabel(f"未知控件: {widget_type}", parent)
            return widget

    @staticmethod
    def get_default_properties(widget_type):
        """获取指定控件类型的默认属性"""
        common_props = {
            "objectName": "",
            "geometry": QRect(0, 0, 100, 30),
        }
        
        if widget_type == "QPushButton":
            specific_props = {
                "text": "按钮",
                "font": None,
                "icon": None,
                "enabled": True,
            }
        
        elif widget_type == "QLabel":
            specific_props = {
                "text": "标签",
                "alignment": Qt.AlignLeft | Qt.AlignVCenter,
                "wordWrap": False,
            }
        
        elif widget_type == "QLineEdit":
            specific_props = {
                "text": "",
                "placeholderText": "请输入文本",
                "maxLength": 32767,
                "readOnly": False,
            }
        
        elif widget_type == "QTextEdit":
            specific_props = {
                "plainText": "",
                "html": "",
                "placeholderText": "请输入多行文本",
                "readOnly": False,
            }
            common_props["geometry"] = QRect(0, 0, 200, 120)
        
        elif widget_type == "QCheckBox":
            specific_props = {
                "text": "复选框",
                "checked": False,
                "tristate": False,
            }
        
        elif widget_type == "QRadioButton":
            specific_props = {
                "text": "单选按钮",
                "checked": False,
            }
        
        elif widget_type == "QComboBox":
            specific_props = {
                "items": ["选项1", "选项2", "选项3"],
                "currentIndex": 0,
                "editable": False,
            }
        
        elif widget_type == "QSpinBox":
            specific_props = {
                "minimum": 0,
                "maximum": 100,
                "value": 50,
                "prefix": "",
                "suffix": "",
            }
        
        elif widget_type == "QSlider":
            specific_props = {
                "minimum": 0,
                "maximum": 100,
                "value": 50,
                "orientation": "horizontal",
                "tickPosition": "NoTicks",
            }
            common_props["geometry"] = QRect(0, 0, 150, 30)
        
        elif widget_type == "QGroupBox":
            specific_props = {
                "title": "分组",
                "checkable": False,
                "checked": False,
            }
            common_props["geometry"] = QRect(0, 0, 200, 150)
        
        elif widget_type == "QTabWidget":
            specific_props = {
                "currentIndex": 0,
                "tabPosition": "North",
                "tabsClosable": False,
            }
            common_props["geometry"] = QRect(0, 0, 250, 180)
        
        elif widget_type == "QTableWidget":
            specific_props = {
                "rowCount": 4,
                "columnCount": 4,
                "horizontalHeaderVisible": True,
                "verticalHeaderVisible": True,
            }
            common_props["geometry"] = QRect(0, 0, 250, 200)
        
        elif widget_type == "QListWidget":
            specific_props = {
                "items": ["项目1", "项目2", "项目3", "项目4"],
                "currentRow": 0,
                "sortingEnabled": False,
            }
            common_props["geometry"] = QRect(0, 0, 150, 180)
        
        else:
            specific_props = {}
        
        # 合并通用属性和特定属性
        return {**common_props, **specific_props}

# 控件工具箱 - 显示可用的积木（控件）
class WidgetBox(QListWidget):
    """控件工具箱 - 显示可拖拽的控件列表（积木库）"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragEnabled(True)
        self.setIconSize(QSize(32, 32))
        self.setSpacing(5)
        self.setViewMode(QListWidget.ListMode)
        self.setAcceptDrops(False)
        
        # 添加所有可用控件
        for widget_type, info in WIDGET_TYPES.items():
            item = QListWidgetItem(info["icon"] + " " + info["text"])
            item.setToolTip(info["description"])
            item.setSizeHint(QSize(100, 40))
            item.setData(Qt.UserRole, widget_type)
            self.addItem(item)
    
    def startDrag(self, supportedActions):
        """开始拖拽操作"""
        item = self.currentItem()
        if not item:
            return
            
        # 获取控件类型及信息
        widget_type = item.data(Qt.UserRole)
        info = WIDGET_TYPES.get(widget_type, {"icon": "", "text": widget_type})
        
        # 预先创建控件实例以获取其尺寸信息
        tmp_widget = WidgetFactory.create_widget(widget_type, None)
        if tmp_widget:
            widget_size = tmp_widget.sizeHint()
            widget_width = max(widget_size.width(), 100)
            widget_height = max(widget_size.height(), 40)
            tmp_widget.deleteLater()  # 清理临时控件
        else:
            widget_width, widget_height = 120, 50  # 默认尺寸
        
        # 创建拖拽数据
        mime_data = QMimeData()
        mime_data.setText(widget_type)
        
        # 创建拖拽对象
        drag = QDrag(self)
        drag.setMimeData(mime_data)
        
        # 创建大尺寸拖拽预览
        # 根据控件实际尺寸调整预览大小，缩放比例1.5
        preview_width = max(240, int(widget_width * 1.5))
        preview_height = max(80, int(widget_height * 1.5))
        
        # 创建更大的透明图像
        pixmap = QPixmap(preview_width, preview_height)
        pixmap.fill(Qt.transparent)
        
        # 初始化绘图对象
        painter = QPainter()
        painter.begin(pixmap)
        painter.setRenderHint(QPainter.Antialiasing, True)  # 启用抗锯齿
        
        # 选择控件类型特定的颜色方案
        # 为每个控件类型定义特定的颜色方案
        gradient = QLinearGradient(0, 0, 0, preview_height)
        
        primary_color = QColor(30, 30, 30, 200)  # 文本颜色
        border_color = QColor(0, 0, 0, 0)        # 边框颜色
        
        # 根据控件类型设置颜色方案
        if "Button" in widget_type:
            # 按钮使用蓝色方案
            gradient.setColorAt(0, QColor(100, 170, 255, 230))
            gradient.setColorAt(1, QColor(50, 120, 220, 230))
            border_color = QColor(40, 90, 180)
        elif "Label" in widget_type:
            # 标签使用绿色方案
            gradient.setColorAt(0, QColor(100, 220, 100, 230))
            gradient.setColorAt(1, QColor(60, 180, 60, 230))
            border_color = QColor(40, 150, 40)
        elif "Edit" in widget_type:
            # 文本编辑框使用白色/浅灰方案
            gradient.setColorAt(0, QColor(250, 250, 250, 230))
            gradient.setColorAt(1, QColor(220, 220, 220, 230))
            border_color = QColor(180, 180, 180)
            primary_color = QColor(60, 60, 60)  # 深色文本
        elif "CheckBox" in widget_type or "Radio" in widget_type:
            # 复选和单选使用紫色方案
            gradient.setColorAt(0, QColor(180, 120, 250, 230))
            gradient.setColorAt(1, QColor(150, 80, 220, 230))
            border_color = QColor(120, 60, 180)
        elif "Combo" in widget_type:
            # 下拉框使用蓝绿色方案
            gradient.setColorAt(0, QColor(100, 200, 220, 230))
            gradient.setColorAt(1, QColor(70, 170, 190, 230))
            border_color = QColor(50, 140, 160)
        elif "Box" in widget_type or "Group" in widget_type:
            # 容器类控件使用紫色方案
            gradient.setColorAt(0, QColor(220, 180, 250, 230))
            gradient.setColorAt(1, QColor(190, 150, 220, 230))
            border_color = QColor(150, 110, 180)
        else:
            # 其他控件使用橙色方案
            gradient.setColorAt(0, QColor(255, 180, 100, 230))
            gradient.setColorAt(1, QColor(240, 140, 60, 230))
            border_color = QColor(200, 100, 40)
        
        # 添加滑动效果和光晕效果
        # 顶部反光
        highlight = QLinearGradient(0, 0, 0, preview_height * 0.4)
        highlight.setColorAt(0, QColor(255, 255, 255, 80))
        highlight.setColorAt(1, QColor(255, 255, 255, 0))
        
        # 绘制主背景和边框
        painter.setPen(QPen(border_color, 2))
        painter.setBrush(gradient)
        main_rect = QRect(4, 4, preview_width-8, preview_height-8)
        painter.drawRoundedRect(main_rect, 14, 14)  # 使用较大的圆角半径
        
        # 绘制顶部反光效果
        painter.setPen(Qt.NoPen)
        painter.setBrush(highlight)
        painter.setOpacity(0.4)  # 降低不透明度
        painter.drawRoundedRect(main_rect, 14, 14)
        painter.setOpacity(1.0)  # 恢复不透明度
        
        # 绘制左右两侧推动箭头
        arrow_pen = QPen(QColor(255, 255, 255, 180), 2)
        painter.setPen(arrow_pen)
        
        # 定义箭头大小
        arrow_size = min(preview_width, preview_height) * 0.2
        
        # 左侧箭头
        left_arrow_x = int(preview_width * 0.15)
        arrow_y = int(preview_height * 0.5)
        arrow_half = int(arrow_size/2)
        
        # 使用整数参数绘制箭头线条
        painter.drawLine(
            int(left_arrow_x + arrow_half), int(arrow_y - arrow_half), 
            int(left_arrow_x - arrow_half), arrow_y
        )
        painter.drawLine(
            int(left_arrow_x - arrow_half), arrow_y, 
            int(left_arrow_x + arrow_half), int(arrow_y + arrow_half)
        )
        
        # 右侧箭头
        right_arrow_x = int(preview_width * 0.85)
        painter.drawLine(
            int(right_arrow_x - arrow_half), int(arrow_y - arrow_half), 
            int(right_arrow_x + arrow_half), arrow_y
        )
        painter.drawLine(
            int(right_arrow_x + arrow_half), arrow_y, 
            int(right_arrow_x - arrow_half), int(arrow_y + arrow_half)
        )
        
        # 准备绘制文本
        text_rect = QRect(int(preview_width * 0.25), 0, int(preview_width * 0.5), preview_height)
        
        # 绘制控件文本
        font = painter.font()
        font.setBold(True)
        font.setPointSize(14)  # 大字体
        painter.setFont(font)
        painter.setPen(QColor(255, 255, 255))  # 白色文本
        
        # 将控件名称和图标居中显示
        text = info["icon"] + " " + info["text"]
        painter.drawText(text_rect, Qt.AlignCenter, text)
        
        # 绘制底部的“拖拽提示”文本
        font.setPointSize(9)
        painter.setFont(font)
        painter.setPen(QColor(255, 255, 255, 160))
        painter.drawText(main_rect, Qt.AlignBottom | Qt.AlignHCenter, "拖动到画布")
        
        # 绘制完成
        painter.end()
        
        # 设置拖拽图标和热点
        drag.setPixmap(pixmap)
        drag.setHotSpot(QPoint(preview_width // 2, preview_height // 2))  # 热点在中心
        
        # 设置拖拽光标
        self.setCursor(Qt.OpenHandCursor)
        
        # 执行拖拽操作
        result = drag.exec_(supportedActions)
        
        # 恢复光标并强制刷新
        self.setCursor(Qt.ArrowCursor)
        self.clearSelection()  # 清除选择以避免残留的选中效果
        self.viewport().update()  # 强制重绘清除残影
        
# 辅助函数：计算文本右对齐位置
def rightMargin(width, painter, text):
    fm = painter.fontMetrics()
    text_width = fm.width(text)
    return width - text_width
