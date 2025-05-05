import sys
import json
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QPushButton, QToolBar, QAction,
                            QDockWidget, QListWidget, QListWidgetItem, QMenu, 
                            QInputDialog, QColorDialog, QFontDialog, QSizePolicy,
                            QScrollArea, QGridLayout, QSpacerItem, QComboBox, 
                            QSpinBox, QLineEdit, QTextEdit, QCheckBox, QRadioButton,
                            QGroupBox, QTabWidget, QFileDialog, QMessageBox, QSlider,
                            QStyle, QStyleFactory, QSplitter, QTableWidget, QTableWidgetItem)
from PyQt5.QtCore import (Qt, QMimeData, QPoint, QSize, QRect, QByteArray,
                          QPropertyAnimation, QEasingCurve, QTimer, pyqtSignal, QEvent)
from PyQt5.QtGui import (QDrag, QPixmap, QPainter, QPen, QColor, QFont,
                         QCursor, QIcon, QFontMetrics, QBrush, QLinearGradient, QPalette)

from components import WidgetFactory, WIDGET_TYPES

# 暗黑主题样式表 - 可根据需要使用
from styles import DARK_STYLESHEET

# 设计画布类 - 接收拖放的控件并支持积木式交互
class DesignCanvas(QWidget):
    """设计画布 - 用于设计GUI界面的工作区，支持拖放、选择、移动等操作"""
    
    widget_selected = pyqtSignal(QWidget)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.widgets = []
        self.selected_widget = None
        self.grid_size = 10
        self.show_grid = True
        self.snap_to_grid_enabled = True
        
        # 调整大小相关属性
        self.resize_handle_size = 8  # 调整大小手柄的大小
        self.resize_mode = False     # 是否处于调整大小模式
        self.resize_edge = None      # 当前调整的边缘
        
        # 拖拽相关属性
        self.drag_indicator = None   # 拖拽时的指示器
        self.drop_indicator_rect = None  # 放置指示器矩形
        self.drag_widget_type = None  # 当前拖拽的控件类型
        
        # 设置最小尺寸
        self.setMinimumSize(800, 600)
        
        # 设置背景色和边框
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(240, 240, 240))
        self.setPalette(palette)
        
        # 安装事件过滤器以捕获鼠标事件
        self.installEventFilter(self)
    
    def dragEnterEvent(self, event):
        """处理拖拽进入事件"""
        if event.mimeData().hasText():
            # 获取控件类型
            self.drag_widget_type = event.mimeData().text()
            
            # 创建拖拽预览
            self.drop_indicator_rect = QRect()
            
            # 接受拖拽操作
            event.acceptProposedAction()
    
    def dragMoveEvent(self, event):
        """处理拖拽移动事件"""
        if event.mimeData().hasText() and self.drag_widget_type:
            # 获取控件默认属性
            properties = WidgetFactory.get_default_properties(self.drag_widget_type)
            geometry = properties["geometry"]
            
            # 计算放置位置（考虑网格对齐）
            drop_pos = event.pos()
            if self.snap_to_grid_enabled:
                drop_pos = self.snap_to_grid(drop_pos)
            
            # 更新放置预览矩形
            rect_width = geometry.width()
            rect_height = geometry.height()
            self.drop_indicator_rect = QRect(
                drop_pos.x(), drop_pos.y(),
                rect_width, rect_height
            )
            
            # 触发重绘以显示预览
            self.update()
            event.acceptProposedAction()
    
    def dropEvent(self, event):
        """处理拖拽放置事件"""
        if event.mimeData().hasText():
            widget_type = event.mimeData().text()
            position = event.pos()
            
            # 创建新控件并添加到画布
            widget = self.create_widget(widget_type, position)
            
            # 添加动画效果 - 使控件稍微放大然后恢复，提供视觉反馈
            if widget:
                animation = QPropertyAnimation(widget, b"geometry")
                animation.setDuration(200)  # 200毫秒
                
                # 起始几何形状（稍微大一点）
                start_geo = widget.geometry()
                large_geo = QRect(
                    start_geo.x() - 5,
                    start_geo.y() - 5,
                    start_geo.width() + 10,
                    start_geo.height() + 10
                )
                
                animation.setStartValue(large_geo)
                animation.setEndValue(start_geo)
                animation.setEasingCurve(QEasingCurve.OutBack)
                animation.start()
            
            # 清除拖拽相关状态
            self.drop_indicator_rect = None
            self.drag_widget_type = None
            self.update()  # 强制重绘清除预览
            
            event.acceptProposedAction()
    
    def create_widget(self, widget_type, position):
        """创建新控件并添加到画布"""
        # 使用工厂创建控件
        widget = WidgetFactory.create_widget(widget_type, self)
        
        # 获取默认属性
        properties = WidgetFactory.get_default_properties(widget_type)
        
        # 设置坐标（考虑网格对齐）
        if self.snap_to_grid_enabled:
            position = self.snap_to_grid(position)
        
        # 更新几何位置
        geometry = properties["geometry"]
        widget.setGeometry(QRect(position.x(), position.y(), 
                                geometry.width(), geometry.height()))
        
        # 确保控件可见
        widget.show()
        
        # 安装事件过滤器以处理控件的交互
        widget.installEventFilter(self)
        
        # 存储控件信息
        widget_info = {
            "widget": widget,
            "widget_type": widget_type,
            "properties": properties
        }
        
        # 添加到控件列表
        self.widgets.append(widget_info)
        
        # 选中新添加的控件
        self.select_widget(widget)
        
        return widget
    
    def select_widget(self, widget):
        """选择一个控件"""
        # 取消之前选择的控件
        if self.selected_widget and self.selected_widget != widget:
            self.update_widget_style(self.selected_widget, False)
        
        # 更新选中的控件
        self.selected_widget = widget
        if widget:
            self.update_widget_style(widget, True)
            self.widget_selected.emit(widget)
    
    def update_widget_style(self, widget, selected):
        """更新控件样式来显示选中状态"""
        if selected:
            widget.setStyleSheet("border: 2px solid #3399ff;")
            widget.setProperty("selected", True)  # 设置自定义属性以在绘制时识别
        else:
            widget.setStyleSheet("")
            widget.setProperty("selected", False)
    
    def snap_to_grid(self, pos):
        """将位置对齐到网格"""
        x = round(pos.x() / self.grid_size) * self.grid_size
        y = round(pos.y() / self.grid_size) * self.grid_size
        return QPoint(x, y)
    
    def paintEvent(self, event):
        """绘制画布背景、网格和调整手柄"""
        super().paintEvent(event)
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)  # 启用抗锯齿
        
        # 绘制网格（如果启用）
        if self.show_grid:
            painter.setPen(QPen(QColor(210, 210, 210), 1, Qt.DotLine))
            
            # 绘制垂直网格线
            for x in range(0, self.width(), self.grid_size):
                painter.drawLine(x, 0, x, self.height())
            
            # 绘制水平网格线
            for y in range(0, self.height(), self.grid_size):
                painter.drawLine(0, y, self.width(), y)
        
        # 绘制拖放预览（如果正在拖放）
        if self.drop_indicator_rect and self.drop_indicator_rect.isValid():
            # 绘制半透明填充
            gradient = QLinearGradient(
                self.drop_indicator_rect.topLeft(),
                self.drop_indicator_rect.bottomRight()
            )
            gradient.setColorAt(0, QColor(0, 120, 215, 60))  # 顶部颜色
            gradient.setColorAt(1, QColor(0, 80, 180, 40))   # 底部颜色
            
            painter.setPen(QPen(QColor(0, 120, 215, 180), 2, Qt.DashLine))
            painter.setBrush(gradient)
            painter.drawRoundedRect(self.drop_indicator_rect, 4, 4)
            
            # 在预览中央绘制控件类型文本
            if self.drag_widget_type:
                widget_info = WIDGET_TYPES.get(self.drag_widget_type, {})
                if widget_info:
                    text = widget_info.get("text", self.drag_widget_type)
                    font = painter.font()
                    font.setBold(True)
                    painter.setFont(font)
                    painter.setPen(QColor(0, 60, 120))
                    painter.drawText(
                        self.drop_indicator_rect, 
                        Qt.AlignCenter, 
                        text
                    )
        
        # 为选中的控件绘制调整大小手柄
        if self.selected_widget:
            # 绘制选中边框 - 使用动画效果的虚线
            pen = QPen(QColor(0, 120, 215), 2)
            pen.setStyle(Qt.DashLine)  # 虚线边框
            painter.setPen(pen)
            painter.setBrush(QColor(0, 120, 215, 15))  # 非常淡的填充
            painter.drawRect(self.selected_widget.geometry())
            
            # 获取控件的几何信息
            geo = self.selected_widget.geometry()
            x = geo.x()
            y = geo.y()
            w = geo.width()
            h = geo.height()
            
            # 设置手柄的画笔和画刷
            painter.setPen(QPen(QColor(0, 120, 215)))
            painter.setBrush(QColor(255, 255, 255))
            
            # 绘制8个调整手柄（左上、上、右上、右、右下、下、左下、左）
            handle_size = self.resize_handle_size
            half_size = handle_size // 2
            
            # 使用圆角矩形绘制手柄，更美观
            def draw_handle(x, y):
                painter.drawRoundedRect(x - half_size, y - half_size, handle_size, handle_size, 2, 2)
            
            # 上方手柄
            draw_handle(x + w // 2, y)
            
            # 右上角手柄
            draw_handle(x + w, y)
            
            # 右侧手柄
            draw_handle(x + w, y + h // 2)
            
            # 右下角手柄
            draw_handle(x + w, y + h)
            
            # 下方手柄
            draw_handle(x + w // 2, y + h)
            
            # 左下角手柄
            draw_handle(x, y + h)
            
            # 左侧手柄
            draw_handle(x, y + h // 2)
            
            # 左上角手柄
            draw_handle(x, y)
    
    # 辅助方法：检测鼠标是否在调整大小的手柄上
    def get_resize_edge(self, widget, pos):
        """检测鼠标是否位于调整大小的手柄上，返回对应的调整方向"""
        if not widget:
            return None
        
        # 获取控件几何信息
        rect = widget.geometry()
        handle_size = self.resize_handle_size
        
        # 检查鼠标是否在各个调整手柄上
        # 左上角
        if abs(pos.x() - rect.left()) <= handle_size and abs(pos.y() - rect.top()) <= handle_size:
            return "top-left"
        # 上边
        elif abs(pos.x() - (rect.left() + rect.width()/2)) <= handle_size and abs(pos.y() - rect.top()) <= handle_size:
            return "top"
        # 右上角
        elif abs(pos.x() - rect.right()) <= handle_size and abs(pos.y() - rect.top()) <= handle_size:
            return "top-right"
        # 右边
        elif abs(pos.x() - rect.right()) <= handle_size and abs(pos.y() - (rect.top() + rect.height()/2)) <= handle_size:
            return "right"
        # 右下角
        elif abs(pos.x() - rect.right()) <= handle_size and abs(pos.y() - rect.bottom()) <= handle_size:
            return "bottom-right"
        # 下边
        elif abs(pos.x() - (rect.left() + rect.width()/2)) <= handle_size and abs(pos.y() - rect.bottom()) <= handle_size:
            return "bottom"
        # 左下角
        elif abs(pos.x() - rect.left()) <= handle_size and abs(pos.y() - rect.bottom()) <= handle_size:
            return "bottom-left"
        # 左边
        elif abs(pos.x() - rect.left()) <= handle_size and abs(pos.y() - (rect.top() + rect.height()/2)) <= handle_size:
            return "left"
        
        return None
    
    def eventFilter(self, obj, event):
        """事件过滤器 - 处理控件的交互"""
        # 处理画布上的鼠标移动事件 - 检测鼠标是否在调整手柄上并改变光标
        if event.type() == QEvent.MouseMove and obj == self and self.selected_widget:
            # 获取鼠标相对于画布的位置
            canvas_pos = event.pos()
            widget_pos = self.selected_widget.pos()
            
            # 转换为相对于控件原点的位置
            local_pos = QPoint(canvas_pos.x() - widget_pos.x(), canvas_pos.y() - widget_pos.y())
            
            # 检测调整边缘
            edge = self.get_resize_edge(self.selected_widget, canvas_pos)
            
            # 根据边缘设置光标形状
            if edge == "top-left" or edge == "bottom-right":
                self.setCursor(Qt.SizeFDiagCursor)
            elif edge == "top-right" or edge == "bottom-left":
                self.setCursor(Qt.SizeBDiagCursor)
            elif edge == "top" or edge == "bottom":
                self.setCursor(Qt.SizeVerCursor)
            elif edge == "left" or edge == "right":
                self.setCursor(Qt.SizeHorCursor)
            else:
                self.setCursor(Qt.ArrowCursor)
        
        # 处理控件的鼠标按下事件
        if event.type() == QEvent.MouseButtonPress and obj != self:
            if event.button() == Qt.LeftButton:
                # 选中点击的控件
                self.select_widget(obj)
                
                # 检查是否点击在调整手柄上
                canvas_pos = obj.mapTo(self, event.pos())
                edge = self.get_resize_edge(obj, canvas_pos)
                
                if edge:
                    # 进入调整大小模式
                    self.resize_mode = True
                    self.resize_edge = edge
                    self.resize_start_pos = canvas_pos
                    self.resize_start_geo = obj.geometry()
                    return True
                
                # 记录点击位置（用于移动）
                obj.drag_start_position = event.pos()
                
                return True
        
        # 处理鼠标释放事件 - 结束调整大小模式
        elif event.type() == QEvent.MouseButtonRelease and event.button() == Qt.LeftButton:
            if self.resize_mode:
                self.resize_mode = False
                self.resize_edge = None
                self.setCursor(Qt.ArrowCursor)
                return True
        
        # 处理画布上的鼠标移动事件 - 实现调整大小
        elif event.type() == QEvent.MouseMove and obj == self and self.resize_mode and self.selected_widget:
            current_pos = event.pos()
            dx = current_pos.x() - self.resize_start_pos.x()
            dy = current_pos.y() - self.resize_start_pos.y()
            
            # 获取初始几何信息
            start_geo = self.resize_start_geo
            new_geo = QRect(start_geo)
            
            # 根据调整方向计算新的几何信息
            if "left" in self.resize_edge:
                # 确保控件不会变得过小
                if start_geo.width() - dx >= 10:
                    new_geo.setLeft(start_geo.left() + dx)
            
            if "right" in self.resize_edge:
                # 确保控件不会变得过小
                if start_geo.width() + dx >= 10:
                    new_geo.setRight(start_geo.right() + dx)
            
            if "top" in self.resize_edge:
                # 确保控件不会变得过小
                if start_geo.height() - dy >= 10:
                    new_geo.setTop(start_geo.top() + dy)
            
            if "bottom" in self.resize_edge:
                # 确保控件不会变得过小
                if start_geo.height() + dy >= 10:
                    new_geo.setBottom(start_geo.bottom() + dy)
            
            # 对齐到网格(如果启用)
            if self.snap_to_grid_enabled:
                # 对齐左上角
                x = round(new_geo.left() / self.grid_size) * self.grid_size
                y = round(new_geo.top() / self.grid_size) * self.grid_size
                
                # 计算边缘对齐后的宽度和高度
                w = round(new_geo.width() / self.grid_size) * self.grid_size
                h = round(new_geo.height() / self.grid_size) * self.grid_size
                
                # 设置新的几何信息，确保最小尺寸
                w = max(w, self.grid_size)
                h = max(h, self.grid_size)
                
                new_geo = QRect(x, y, w, h)
            
            # 应用新几何信息
            self.selected_widget.setGeometry(new_geo)
            
            # 更新存储的属性
            for w in self.widgets:
                if w['widget'] == self.selected_widget:
                    w['properties']['geometry'] = new_geo
                    break
            
            # 强制重绘以显示调整手柄
            self.update()
            
            return True
        
        # 处理控件的鼠标移动事件 - 实现拖拽移动
        elif event.type() == QEvent.MouseMove and obj != self:
            if hasattr(obj, 'drag_start_position') and \
               (event.pos() - obj.drag_start_position).manhattanLength() > 10 and \
               not self.resize_mode:
                # 移动控件
                if self.selected_widget == obj:
                    # 获取鼠标在父控件中的位置
                    parent_pos = obj.mapToParent(event.pos() - obj.drag_start_position)
                    
                    # 对齐到网格（如果启用）
                    if self.snap_to_grid_enabled:
                        parent_pos = self.snap_to_grid(parent_pos)
                    
                    # 移动控件
                    obj.move(parent_pos)
                    
                    # 更新存储的属性
                    for w in self.widgets:
                        if w['widget'] == obj:
                            w['properties']['geometry'] = obj.geometry()
                            break
                    
                    return True
        
        # 处理控件的右键菜单事件
        elif event.type() == QEvent.ContextMenu and obj != self:
            # 显示上下文菜单
            self.show_context_menu(obj, event.globalPos())
            return True
        
        # 处理画布的右键菜单事件
        elif event.type() == QEvent.ContextMenu and obj == self:
            # 画布右键菜单：添加控件、粘贴等
            menu = QMenu(self)
            
            # 添加控件子菜单
            add_menu = menu.addMenu("添加控件")
            for widget_type, info in WIDGET_TYPES.items():
                action = add_menu.addAction(info["icon"] + " " + info["text"])
                action.setData(widget_type)
                action.triggered.connect(lambda checked, wt=widget_type: 
                                       self.create_widget(wt, self.mapFromGlobal(QCursor.pos())))
            
            # 显示菜单
            menu.exec_(event.globalPos())
            return True
        
        return super().eventFilter(obj, event)
    
    def show_context_menu(self, widget, pos):
        """显示控件的上下文菜单"""
        menu = QMenu(self)
        
        # 编辑属性
        edit_action = menu.addAction("编辑属性")
        edit_action.triggered.connect(lambda: self.edit_widget_properties(widget))
        
        # 复制控件
        copy_action = menu.addAction("复制")
        copy_action.triggered.connect(lambda: self.copy_widget(widget))
        
        # 删除控件
        delete_action = menu.addAction("删除")
        delete_action.triggered.connect(lambda: self.delete_widget(widget))
        
        # 显示菜单
        menu.exec_(pos)
    
    def edit_widget_properties(self, widget):
        """编辑控件属性"""
        # 通知属性编辑器显示该控件的属性
        self.widget_selected.emit(widget)
    
    def delete_widget(self, widget):
        """删除控件"""
        # 从列表中移除
        for i, w in enumerate(self.widgets):
            if w['widget'] == widget:
                self.widgets.pop(i)
                break
        
        # 取消选择
        if self.selected_widget == widget:
            self.selected_widget = None
        
        # 删除控件
        widget.deleteLater()
    
    def copy_widget(self, widget):
        """复制一个控件"""
        # 找到控件信息
        widget_info = None
        for w in self.widgets:
            if w['widget'] == widget:
                widget_info = w
                break
        
        if not widget_info:
            return
        
        # 计算新位置（偏移一点）
        old_pos = widget.pos()
        new_pos = QPoint(old_pos.x() + 20, old_pos.y() + 20)
        
        # 创建新控件
        new_widget = self.create_widget(widget_info['widget_type'], new_pos)
        
        # 复制属性（除了几何位置，因为我们已经设置了新位置）
        for prop_name, value in widget_info['properties'].items():
            if prop_name != 'geometry' and hasattr(new_widget, f"set{prop_name[0].upper()}{prop_name[1:]}"):
                try:
                    getattr(new_widget, f"set{prop_name[0].upper()}{prop_name[1:]}")(*value)
                except:
                    try:
                        getattr(new_widget, f"set{prop_name[0].upper()}{prop_name[1:]}")(*value)
                    except:
                        pass
        
        # 选中新控件
        self.select_widget(new_widget)

# 属性编辑器类 - 编辑选中控件的属性
class PropertyEditor(QScrollArea):
    """属性编辑器 - 用于编辑选中控件的属性"""
    
    property_changed = pyqtSignal(str, object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_widget = None
        self.properties = {}
        
        # 主布局
        self.widget = QWidget()
        self.layout = QVBoxLayout(self.widget)
        self.layout.setSpacing(5)
        self.layout.setContentsMargins(5, 5, 5, 5)
        
        # 设置滚动区域
        self.setWidget(self.widget)
        self.setWidgetResizable(True)
        self.setMinimumWidth(250)
        
        # 标题标签
        self.title_label = QLabel("属性编辑器")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.layout.addWidget(self.title_label)
        
        # 属性容器
        self.prop_container = QWidget()
        self.prop_layout = QVBoxLayout(self.prop_container)
        self.prop_layout.setSpacing(10)
        self.prop_layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.prop_container)
        
        # 添加弹性空间
        self.layout.addStretch(1)
    
    def update_properties(self, widget, widget_info=None):
        """更新属性编辑器以显示选中控件的属性"""
        # 清除现有属性
        self.clear_properties()
        
        # 更新当前控件
        self.current_widget = widget
        
        if not widget:
            return
        
        # 查找控件信息
        if not widget_info:
            for w in self.window().canvas.widgets:
                if w['widget'] == widget:
                    widget_info = w
                    break
        
        if not widget_info:
            return
        
        # 更新标题
        self.title_label.setText(f"属性编辑器 - {widget_info['widget_type']}")
        
        # 保存属性引用
        self.properties = widget_info['properties']
        
        # 按组添加属性
        # 基本属性组
        basic_props = ["objectName", "geometry"]
        self.add_property_group("基本属性", basic_props)
        
        # 特定控件属性
        widget_type = widget_info['widget_type']
        
        if widget_type == "QPushButton":
            specific_props = ["text", "enabled"]
            self.add_property_group("按钮属性", specific_props)
        
        elif widget_type == "QLabel":
            specific_props = ["text", "alignment", "wordWrap"]
            self.add_property_group("标签属性", specific_props)
        
        elif widget_type == "QLineEdit":
            specific_props = ["text", "placeholderText", "maxLength", "readOnly"]
            self.add_property_group("文本框属性", specific_props)
        
        elif widget_type == "QTextEdit":
            specific_props = ["plainText", "html", "placeholderText", "readOnly"]
            self.add_property_group("多行文本框属性", specific_props)
        
        elif widget_type == "QCheckBox" or widget_type == "QRadioButton":
            specific_props = ["text", "checked"]
            if widget_type == "QCheckBox":
                specific_props.append("tristate")
            self.add_property_group("选择框属性", specific_props)
        
        elif widget_type == "QComboBox":
            specific_props = ["items", "currentIndex", "editable"]
            self.add_property_group("下拉框属性", specific_props)
        
        elif widget_type == "QSpinBox":
            specific_props = ["minimum", "maximum", "value", "prefix", "suffix"]
            self.add_property_group("数字框属性", specific_props)
        
        elif widget_type == "QSlider":
            specific_props = ["minimum", "maximum", "value", "orientation", "tickPosition"]
            self.add_property_group("滑块属性", specific_props)
        
        elif widget_type == "QGroupBox":
            specific_props = ["title", "checkable", "checked"]
            self.add_property_group("分组框属性", specific_props)
        
        elif widget_type == "QTabWidget":
            specific_props = ["currentIndex", "tabPosition", "tabsClosable"]
            self.add_property_group("选项卡属性", specific_props)
        
        elif widget_type == "QTableWidget":
            specific_props = ["rowCount", "columnCount", "horizontalHeaderVisible", "verticalHeaderVisible"]
            self.add_property_group("表格属性", specific_props)
        
        elif widget_type == "QListWidget":
            specific_props = ["items", "currentRow", "sortingEnabled"]
            self.add_property_group("列表属性", specific_props)
    
    def add_property_group(self, group_name, properties):
        """添加一组属性到编辑器中"""
        # 创建分组标签
        group_label = QLabel(group_name)
        group_label.setStyleSheet("font-weight: bold; color: #555; background-color: #f0f0f0; padding: 3px;")
        self.prop_layout.addWidget(group_label)
        
        # 添加属性
        for prop in properties:
            if prop in self.properties:
                # 创建编辑器
                self.create_property_editor(prop)
        
        # 添加分隔符
        separator = QLabel()
        separator.setStyleSheet("min-height: 1px; max-height: 1px; background-color: #e0e0e0;")
        self.prop_layout.addWidget(separator)
    
    def create_property_editor(self, prop):
        """为特定属性创建编辑器控件"""
        # 属性值
        value = self.properties.get(prop)
        if value is None:
            return
        
        # 属性容器
        prop_widget = QWidget()
        prop_layout = QHBoxLayout(prop_widget)
        prop_layout.setContentsMargins(0, 5, 0, 5)
        
        # 属性名标签
        name_label = QLabel(prop)
        name_label.setMinimumWidth(100)
        prop_layout.addWidget(name_label)
        
        # 基于属性类型创建不同的编辑器
        editor = None
        
        # 几何属性特殊处理
        if prop == "geometry":
            # 创建几何编辑器
            geometry = value
            geo_layout = QHBoxLayout()
            
            # X坐标
            x_spin = QSpinBox()
            x_spin.setRange(0, 10000)
            x_spin.setValue(geometry.x())
            x_spin.setPrefix("X: ")
            x_spin.valueChanged.connect(lambda v: self.update_geometry(v, geometry.y(), geometry.width(), geometry.height()))
            geo_layout.addWidget(x_spin)
            
            # Y坐标
            y_spin = QSpinBox()
            y_spin.setRange(0, 10000)
            y_spin.setValue(geometry.y())
            y_spin.setPrefix("Y: ")
            y_spin.valueChanged.connect(lambda v: self.update_geometry(geometry.x(), v, geometry.width(), geometry.height()))
            geo_layout.addWidget(y_spin)
            
            # 宽度
            w_spin = QSpinBox()
            w_spin.setRange(1, 10000)
            w_spin.setValue(geometry.width())
            w_spin.setPrefix("宽: ")
            w_spin.valueChanged.connect(lambda v: self.update_geometry(geometry.x(), geometry.y(), v, geometry.height()))
            geo_layout.addWidget(w_spin)
            
            # 高度
            h_spin = QSpinBox()
            h_spin.setRange(1, 10000)
            h_spin.setValue(geometry.height())
            h_spin.setPrefix("高: ")
            h_spin.valueChanged.connect(lambda v: self.update_geometry(geometry.x(), geometry.y(), geometry.width(), v))
            geo_layout.addWidget(h_spin)
            
            geo_widget = QWidget()
            geo_widget.setLayout(geo_layout)
            prop_layout.addWidget(geo_widget)
        
        # 字符串
        elif isinstance(value, str):
            editor = QLineEdit(value)
            editor.textChanged.connect(lambda text: self.property_changed.emit(prop, text))
            prop_layout.addWidget(editor)
        
        # 整数
        elif isinstance(value, int):
            editor = QSpinBox()
            editor.setRange(-999999, 999999)
            editor.setValue(value)
            editor.valueChanged.connect(lambda val: self.property_changed.emit(prop, val))
            prop_layout.addWidget(editor)
        
        # 浮点数
        elif isinstance(value, float):
            editor = QDoubleSpinBox()
            editor.setRange(-999999, 999999)
            editor.setValue(value)
            editor.valueChanged.connect(lambda val: self.property_changed.emit(prop, val))
            prop_layout.addWidget(editor)
        
        # 布尔值
        elif isinstance(value, bool):
            editor = QCheckBox()
            editor.setChecked(value)
            editor.stateChanged.connect(lambda state: self.property_changed.emit(prop, state == Qt.Checked))
            prop_layout.addWidget(editor)
        
        # 字符串列表
        elif isinstance(value, list) and (not value or isinstance(value[0], str)):
            editor = QLineEdit(", ".join(value))
            edit_button = QPushButton("编辑...")
            edit_button.clicked.connect(lambda: self.edit_string_list(prop))
            
            prop_layout.addWidget(editor, 1)
            prop_layout.addWidget(edit_button)
            
            # 禁用直接编辑，使用编辑按钮
            editor.setReadOnly(True)
        
        # 字体
        elif prop == "font":
            button = QPushButton("选择字体...")
            button.clicked.connect(lambda: self.select_font(prop))
            prop_layout.addWidget(button)
        
        # 颜色
        elif prop == "color" or prop == "backgroundColor":
            button = QPushButton("选择颜色...")
            button.clicked.connect(lambda: self.select_color(prop))
            
            # 如果有颜色，显示预览
            if isinstance(value, QColor) and value.isValid():
                color_preview = QLabel()
                color_preview.setFixedSize(20, 20)
                color_preview.setStyleSheet(f"background-color: {value.name()}; ")
                prop_layout.addWidget(color_preview)
            
            prop_layout.addWidget(button)
        
        # 对齐方式
        elif prop == "alignment":
            combo = QComboBox()
            alignments = [
                ("左对齐", Qt.AlignLeft),
                ("居中对齐", Qt.AlignCenter),
                ("右对齐", Qt.AlignRight),
                ("顶部对齐", Qt.AlignTop),
                ("垂直居中", Qt.AlignVCenter),
                ("底部对齐", Qt.AlignBottom)
            ]
            
            for name, align in alignments:
                combo.addItem(name, align)
            
            # 设置当前值
            for i, (name, align) in enumerate(alignments):
                if value & align:
                    combo.setCurrentIndex(i)
                    break
            
            combo.currentIndexChanged.connect(
                lambda idx: self.property_changed.emit(prop, combo.itemData(idx))
            )
            prop_layout.addWidget(combo)
        
        # 方向（水平、垂直）
        elif prop == "orientation":
            combo = QComboBox()
            combo.addItem("水平", "horizontal")
            combo.addItem("垂直", "vertical")
            
            combo.setCurrentIndex(0 if value == "horizontal" else 1)
            combo.currentIndexChanged.connect(
                lambda idx: self.property_changed.emit(prop, combo.itemData(idx))
            )
            prop_layout.addWidget(combo)
        
        # 添加属性编辑器到布局
        self.prop_layout.addWidget(prop_widget)
    
    def update_geometry(self, x, y, width, height):
        """更新几何属性"""
        if self.current_widget:
            self.current_widget.setGeometry(x, y, width, height)
            self.property_changed.emit("geometry", QRect(x, y, width, height))
    
    def select_font(self, prop_name):
        """选择字体"""
        if self.current_widget:
            current_font = self.properties.get(prop_name) or self.current_widget.font()
            font, ok = QFontDialog.getFont(current_font, self, "选择字体")
            
            if ok:
                self.current_widget.setFont(font)
                self.property_changed.emit(prop_name, font)
    
    def select_color(self, prop_name):
        """选择颜色"""
        if self.current_widget:
            # 获取当前颜色
            current_color = self.properties.get(prop_name)
            if not current_color or not isinstance(current_color, QColor):
                current_color = QColor(Qt.black)
            
            # 显示颜色对话框
            color = QColorDialog.getColor(current_color, self, "选择颜色")
            
            if color.isValid():
                # 根据属性类型设置颜色
                if prop_name == "color":
                    palette = self.current_widget.palette()
                    palette.setColor(QPalette.WindowText, color)
                    self.current_widget.setPalette(palette)
                elif prop_name == "backgroundColor":
                    palette = self.current_widget.palette()
                    palette.setColor(QPalette.Window, color)
                    self.current_widget.setPalette(palette)
                
                # 发出属性改变信号
                self.property_changed.emit(prop_name, color)
    
    def edit_string_list(self, prop_name):
        """编辑字符串列表"""
        if self.current_widget:
            # 获取当前列表
            current_list = self.properties.get(prop_name, [])
            
            # 显示编辑对话框
            text, ok = QInputDialog.getMultiLineText(
                self, f"编辑{prop_name}", 
                "每行输入一个项目：", 
                "\n".join(current_list)
            )
            
            if ok:
                # 更新列表
                new_list = [line.strip() for line in text.split("\n") if line.strip()]
                
                # 更新界面和属性
                if prop_name == "items":
                    if hasattr(self.current_widget, "clear") and hasattr(self.current_widget, "addItems"):
                        self.current_widget.clear()
                        self.current_widget.addItems(new_list)
                
                # 发出属性改变信号
                self.property_changed.emit(prop_name, new_list)
    
    def clear_properties(self):
        """清除属性编辑器"""
        # 清除属性布局中的所有控件
        while self.prop_layout.count():
            item = self.prop_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

# 代码生成器类 - 生成 PyQt5 代码
class CodeGenerator:
    """代码生成器 - 生成 PyQt5 代码和 UI 文件"""
    
    def __init__(self, canvas):
        self.canvas = canvas
    
    def generate_python_code(self):
        """生成 Python 代码"""
        widgets = self.canvas.widgets
        if not widgets:
            return "# 没有控件可以生成代码"
        
        # 生成导入语句
        imports = [
            "import sys",
            "from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,",
            "                           QHBoxLayout, QLabel, QPushButton, QGroupBox,",
            "                           QLineEdit, QTextEdit, QCheckBox, QRadioButton,",
            "                           QComboBox, QSpinBox, QSlider, QTableWidget,",
            "                           QTabWidget, QListWidget)",
            "from PyQt5.QtCore import Qt, QRect",
            "from PyQt5.QtGui import QFont, QIcon",
            ""
        ]
        
        # 导入所需的特定控件
        widget_types = set(w['widget_type'] for w in widgets)
        
        # 主窗口类定义
        class_code = [
            "class MyWindow(QMainWindow):",
            "    def __init__(self):",
            "        super().__init__()",
            "        self.init_ui()",
            "",
            "    def init_ui(self):",
            "        # 设置窗口基本属性",
            "        self.setWindowTitle('PyQt5 GUI 应用')",
            "        self.setGeometry(100, 100, 800, 600)",
            "",
            "        # 创建中央控件",
            "        self.central_widget = QWidget()",
            "        self.setCentralWidget(self.central_widget)",
            "",
            "        # 设置布局",
            "        self.layout = QVBoxLayout(self.central_widget)",
            "        self.layout.setContentsMargins(10, 10, 10, 10)",
            ""
        ]
        
        # 控件创建代码
        setup_code = []
        for i, w in enumerate(widgets):
            widget = w['widget']
            widget_type = w['widget_type']
            properties = w['properties']
            var_name = f"self.{widget_type.lower()}_{i+1}"
            
            # 创建控件
            setup_code.append(f"        # 创建 {widget_type}")
            setup_code.append(f"        {var_name} = {widget_type}(self.central_widget)")
            
            # 设置几何属性
            geometry = properties.get('geometry')
            if geometry:
                x, y, width, height = geometry.x(), geometry.y(), geometry.width(), geometry.height()
                setup_code.append(f"        {var_name}.setGeometry(QRect({x}, {y}, {width}, {height}))")
            
            # 设置对象名称
            obj_name = properties.get('objectName')
            if obj_name:
                setup_code.append(f"        {var_name}.setObjectName('{obj_name}')")
            
            # 设置特定属性
            if 'text' in properties and hasattr(widget, 'setText'):
                text = properties['text']
                setup_code.append(f"        {var_name}.setText('{text}')")
            
            if 'placeholderText' in properties and hasattr(widget, 'setPlaceholderText'):
                placeholder = properties['placeholderText']
                setup_code.append(f"        {var_name}.setPlaceholderText('{placeholder}')")
            
            if 'checked' in properties and hasattr(widget, 'setChecked'):
                checked = properties['checked']
                setup_code.append(f"        {var_name}.setChecked({checked})")
            
            if 'items' in properties and hasattr(widget, 'addItems'):
                items = properties['items']
                items_str = "[" + ", ".join([f"'{item}'" for item in items]) + "]"
                setup_code.append(f"        {var_name}.addItems({items_str})")
            
            if 'minimum' in properties and hasattr(widget, 'setMinimum'):
                minimum = properties['minimum']
                setup_code.append(f"        {var_name}.setMinimum({minimum})")
            
            if 'maximum' in properties and hasattr(widget, 'setMaximum'):
                maximum = properties['maximum']
                setup_code.append(f"        {var_name}.setMaximum({maximum})")
            
            if 'value' in properties and hasattr(widget, 'setValue'):
                value = properties['value']
                setup_code.append(f"        {var_name}.setValue({value})")
            
            if 'orientation' in properties and hasattr(widget, 'setOrientation'):
                orientation = properties['orientation']
                if orientation.lower() == 'horizontal':
                    setup_code.append(f"        {var_name}.setOrientation(Qt.Horizontal)")
                else:
                    setup_code.append(f"        {var_name}.setOrientation(Qt.Vertical)")
            
            if 'title' in properties and hasattr(widget, 'setTitle'):
                title = properties['title']
                setup_code.append(f"        {var_name}.setTitle('{title}')")
            
            # 添加到布局
            setup_code.append(f"        self.layout.addWidget({var_name})")
            setup_code.append("")
        
        # 主函数代码
        main_code = [
            "# 主函数",
            "def main():",
            "    app = QApplication(sys.argv)",
            "    window = MyWindow()",
            "    window.show()",
            "    sys.exit(app.exec_())",
            "",
            "if __name__ == '__main__':",
            "    main()"
        ]
        
        # 组合所有代码
        all_code = imports + [""] + class_code + setup_code + [""] + main_code
        return "\n".join(all_code)
    
    def generate_ui_code(self):
        """生成 Qt Designer UI 文件格式的 XML 代码"""
        widgets = self.canvas.widgets
        if not widgets:
            return "<!-- 没有控件可以生成 UI 文件 -->"
        
        # 开始 XML
        ui_code = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<ui version="4.0">',
            ' <class>MainWindow</class>',
            ' <widget class="QMainWindow" name="MainWindow">',
            '  <property name="geometry">',
            '   <rect>',
            '    <x>0</x>',
            '    <y>0</y>',
            '    <width>800</width>',
            '    <height>600</height>',
            '   </rect>',
            '  </property>',
            '  <property name="windowTitle">',
            '   <string>PyQt5 GUI 应用</string>',
            '  </property>',
            '  <widget class="QWidget" name="centralwidget">',
        ]
        
        # 生成各个控件的 XML
        for i, w in enumerate(widgets):
            widget = w['widget']
            widget_type = w['widget_type']
            properties = w['properties']
            geometry = properties.get('geometry')
            obj_name = properties.get('objectName') or f"{widget_type.lower()}_{i+1}"
            
            ui_code.extend([
                f'   <widget class="{widget_type}" name="{obj_name}">',
                '    <property name="geometry">',
                '     <rect>',
                f'      <x>{geometry.x()}</x>',
                f'      <y>{geometry.y()}</y>',
                f'      <width>{geometry.width()}</width>',
                f'      <height>{geometry.height()}</height>',
                '     </rect>',
                '    </property>',
            ])
            
            # 添加其他属性
            if 'text' in properties and hasattr(widget, 'text'):
                ui_code.extend([
                    '    <property name="text">',
                    f'     <string>{properties["text"]}</string>',
                    '    </property>',
                ])
            
            if 'placeholderText' in properties and hasattr(widget, 'placeholderText'):
                ui_code.extend([
                    '    <property name="placeholderText">',
                    f'     <string>{properties["placeholderText"]}</string>',
                    '    </property>',
                ])
            
            if 'checked' in properties and hasattr(widget, 'isChecked'):
                ui_code.extend([
                    '    <property name="checked">',
                    f'     <bool>{"true" if properties["checked"] else "false"}</bool>',
                    '    </property>',
                ])
            
            # 关闭控件标签
            ui_code.append('   </widget>')
        
        # 完成 UI 文件
        ui_code.extend([
            '  </widget>',
            '  <menubar name="menubar"/>',
            '  <statusbar name="statusbar"/>',
            ' </widget>',
            ' <resources/>',
            ' <connections/>',
            '</ui>'
        ])
        
        return "\n".join(ui_code)
