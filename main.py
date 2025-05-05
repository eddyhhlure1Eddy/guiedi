import sys
import json
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QPushButton, QToolBar, QAction,
                            QDockWidget, QMenu, QInputDialog, QFileDialog, QMessageBox,
                            QSplitter, QComboBox)
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QIcon

# 导入自定义模块
from components import WidgetBox, WIDGET_TYPES
from designer import DesignCanvas, PropertyEditor, CodeGenerator
from styles import DARK_STYLESHEET, BLOCKS_LIGHT_STYLESHEET

# 主应用程序类
class PyQtDesigner(QMainWindow):
    """主窗口类 - 集成控件库、设计画布、属性编辑器等组件"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """初始化用户界面"""
        # 设置窗口基本属性
        self.setWindowTitle("PyQt5 可视化设计器")
        self.setGeometry(100, 100, 1200, 800)
        
        # 创建并设置菜单栏
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件")
        
        new_action = QAction("新建项目", self)
        new_action.triggered.connect(self.new_project)
        file_menu.addAction(new_action)
        
        open_action = QAction("打开项目", self)
        open_action.triggered.connect(self.open_project)
        file_menu.addAction(open_action)
        
        save_action = QAction("保存项目", self)
        save_action.triggered.connect(self.save_project)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 代码菜单
        code_menu = menubar.addMenu("代码")
        
        generate_action = QAction("生成代码", self)
        generate_action.triggered.connect(self.generate_code)
        code_menu.addAction(generate_action)
        
        export_action = QAction("导出代码", self)
        export_action.triggered.connect(self.export_code)
        code_menu.addAction(export_action)
        
        # u521bu5efau5de5u5177u680f
        self.create_toolbar()
        
        # u521bu5efau4e3bu5e03u5c40
        self.main_splitter = QSplitter(Qt.Horizontal)
        self.setCentralWidget(self.main_splitter)
        
        # 创建控件库 Dock 窗口
        widget_dock = QDockWidget("控件库", self)
        widget_dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        widget_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        
        # 创建控件库
        self.widget_box = WidgetBox()
        self.widget_box.setObjectName("widget_box")
        widget_dock.setWidget(self.widget_box)
        
        # 添加 Dock 窗口到主窗口
        self.addDockWidget(Qt.LeftDockWidgetArea, widget_dock)
        
        # 创建设计画布
        self.canvas = DesignCanvas()
        self.canvas.setObjectName("design_canvas")
        
        # 创建代码生成器
        self.code_generator = CodeGenerator(self.canvas)
        
        # 创建属性编辑器
        self.property_editor = PropertyEditor()
        
        # 将画布选中信号连接到属性编辑器
        self.canvas.widget_selected.connect(self.property_editor.update_properties)
        
        # 将属性变更信号连接到处理函数
        self.property_editor.property_changed.connect(self.on_property_changed)
        
        # 将组件添加到主拖分器
        self.main_splitter.addWidget(self.canvas)
        
        # 创建属性编辑器 Dock 窗口
        prop_dock = QDockWidget("属性编辑器", self)
        prop_dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        prop_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        prop_dock.setWidget(self.property_editor)
        
        # 添加属性编辑器 Dock 窗口
        self.addDockWidget(Qt.RightDockWidgetArea, prop_dock)
        
        # 设置状态栏
        self.statusBar().showMessage("就绪完毕 - 请从左侧选择控件并拖拽到画布")
        
        # 应用样式表
        self.setStyleSheet(BLOCKS_LIGHT_STYLESHEET)
        
        # 默认拖放网格和网格大小
        self.canvas.show_grid = True
        self.canvas.grid_size = 10
    
    def create_toolbar(self):
        """创建工具栏"""
        # 主工具栏
        toolbar = self.addToolBar("工具栏")
        toolbar.setMovable(True)
        toolbar.setIconSize(QSize(24, 24))
        
        # 新建项目按钮
        new_action = QAction("新建", self)
        new_action.setStatusTip("创建新项目")
        new_action.triggered.connect(self.new_project)
        toolbar.addAction(new_action)
        
        # 打开项目按钮
        open_action = QAction("打开", self)
        open_action.setStatusTip("打开现有项目")
        open_action.triggered.connect(self.open_project)
        toolbar.addAction(open_action)
        
        # 保存项目按钮
        save_action = QAction("保存", self)
        save_action.setStatusTip("保存当前项目")
        save_action.triggered.connect(self.save_project)
        toolbar.addAction(save_action)
        
        toolbar.addSeparator()
        
        # 删除选中控件按钮
        delete_action = QAction("删除", self)
        delete_action.setStatusTip("删除选中的控件")
        delete_action.triggered.connect(self.delete_selected)
        toolbar.addAction(delete_action)
        
        toolbar.addSeparator()
        
        # 网格控制
        grid_action = QAction("显示网格", self)
        grid_action.setCheckable(True)
        grid_action.setChecked(True)
        grid_action.setStatusTip("显示/隐藏网格")
        grid_action.triggered.connect(self.toggle_grid)
        toolbar.addAction(grid_action)
        
        # 网格大小选择
        grid_size_label = QLabel("网格大小: ")
        toolbar.addWidget(grid_size_label)
        
        grid_size_combo = QComboBox()
        grid_size_combo.addItems(["5", "10", "15", "20", "25", "30"])
        grid_size_combo.setCurrentIndex(1)  # 默认为10
        grid_size_combo.currentTextChanged.connect(self.change_grid_size)
        toolbar.addWidget(grid_size_combo)
        
        toolbar.addSeparator()
        
        # 生成代码按钮
        code_action = QAction("生成代码", self)
        code_action.setStatusTip("生成并预览代码")
        code_action.triggered.connect(self.generate_code)
        toolbar.addAction(code_action)
        
        # 导出代码按钮
        export_action = QAction("导出代码", self)
        export_action.setStatusTip("导出代码到文件")
        export_action.triggered.connect(self.export_code)
        toolbar.addAction(export_action)
    
    def new_project(self):
        """创建新项目"""
        # 询问用户是否保存当前项目
        if self.canvas.widgets:
            reply = QMessageBox.question(
                self, "新建项目", "是否保存当前项目？",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Save
            )
            
            if reply == QMessageBox.Save:
                self.save_project()
            elif reply == QMessageBox.Cancel:
                return
        
        # 清空当前画布
        for w in self.canvas.widgets[::]:
            self.canvas.delete_widget(w['widget'])
        
        # 清空属性编辑器
        self.property_editor.clear_properties()
        self.canvas.selected_widget = None
        
        # 更新状态栏
        self.statusBar().showMessage("已创建新项目")
    
    def open_project(self):
        """打开项目"""
        # 选择项目文件
        file_name, _ = QFileDialog.getOpenFileName(
            self, "打开项目", "", "PyQt设计器文件 (*.pqd);;所有文件 (*)"
        )
        
        if not file_name:
            return
        
        try:
            # 读取项目文件
            with open(file_name, 'r', encoding='utf-8') as f:
                project_data = json.load(f)
            
            # 清空当前画布
            for w in self.canvas.widgets[::]:
                self.canvas.delete_widget(w['widget'])
            
            # 清空属性编辑器
            self.property_editor.clear_properties()
            self.canvas.selected_widget = None
            
            # 加载控件
            for widget_data in project_data['widgets']:
                widget_type = widget_data['widget_type']
                properties = widget_data['properties']
                
                # 从几何属性中恢复位置
                geometry = properties.get('geometry', {})
                if isinstance(geometry, dict):
                    position = QPoint(geometry.get('x', 0), geometry.get('y', 0))
                else:
                    position = QPoint(geometry.x(), geometry.y())
                
                # 创建控件
                widget = self.canvas.create_widget(widget_type, position)
                
                # 应用属性
                for prop_name, value in properties.items():
                    self.on_property_changed(prop_name, value)
            
            # 更新状态栏
            self.statusBar().showMessage(f"已打开项目: {file_name}")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"打开项目失败: {str(e)}")
    
    def save_project(self):
        """保存项目"""
        # 选择保存文件路径
        file_name, _ = QFileDialog.getSaveFileName(
            self, "保存项目", "", "PyQt设计器文件 (*.pqd);;所有文件 (*)"
        )
        
        if not file_name:
            return
        
        # 确保文件有正确的扩展名
        if not file_name.endswith('.pqd'):
            file_name += '.pqd'
        
        try:
            # 构建项目数据
            project_data = {
                'version': '1.0',
                'widgets': []
            }
            
            # 保存所有控件数据
            for w in self.canvas.widgets:
                widget_data = {
                    'widget_type': w['widget_type'],
                    'properties': w['properties']
                }
                project_data['widgets'].append(widget_data)
            
            # 写入文件
            with open(file_name, 'w', encoding='utf-8') as f:
                json.dump(project_data, f, indent=4, ensure_ascii=False)
            
            # 更新状态栏
            self.statusBar().showMessage(f"已保存项目到: {file_name}")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存项目失败: {str(e)}")
    
    def toggle_grid(self, checked):
        """切换网格显示"""
        self.canvas.show_grid = checked
        self.canvas.update()
    
    def change_grid_size(self, size_text):
        """更改网格大小"""
        try:
            self.canvas.grid_size = int(size_text)
            self.canvas.update()
        except ValueError:
            pass
    
    def delete_selected(self):
        """删除选中的控件"""
        if self.canvas.selected_widget:
            self.canvas.delete_widget(self.canvas.selected_widget)
    
    def generate_code(self):
        """生成代码并显示"""
        if not self.canvas.widgets:
            QMessageBox.information(self, "提示", "没有控件可以生成代码")
            return
        
        # 生成Python代码
        python_code = self.code_generator.generate_python_code()
        
        # 显示代码预览对话框
        dialog = QMessageBox(self)
        dialog.setWindowTitle("生成的Python代码")
        dialog.setText("已成功生成Python代码！")
        dialog.setDetailedText(python_code)
        dialog.setStandardButtons(QMessageBox.Ok | QMessageBox.Save)
        dialog.setDefaultButton(QMessageBox.Ok)
        
        result = dialog.exec_()
        
        # 导出代码
        if result == QMessageBox.Save:
            self.export_code()
    
    def export_code(self):
        """导出代码到文件"""
        # 生成代码
        python_code = self.code_generator.generate_python_code()
        ui_code = self.code_generator.generate_ui_code()
        
        # 选择导出格式
        formats = ["Python 脚本 (*.py)", "Qt UI 文件 (*.ui)"]
        format_choice, ok = QInputDialog.getItem(
            self, "选择导出格式", "选择导出格式:", formats, 0, False
        )
        
        if not ok:
            return
        
        # 保存文件
        if format_choice == formats[0]:  # Python 脚本
            file_name, _ = QFileDialog.getSaveFileName(
                self, "导出 Python 代码", "", "Python 文件 (*.py);;所有文件 (*)"
            )
            
            if file_name:
                if not file_name.endswith('.py'):
                    file_name += '.py'
                
                try:
                    with open(file_name, 'w', encoding='utf-8') as f:
                        f.write(python_code)
                    
                    self.statusBar().showMessage(f"已导出 Python 代码: {file_name}")
                
                except Exception as e:
                    QMessageBox.critical(self, "错误", f"导出代码失败: {str(e)}")
        
        elif format_choice == formats[1]:  # Qt UI 文件
            file_name, _ = QFileDialog.getSaveFileName(
                self, "导出 UI 文件", "", "UI 文件 (*.ui);;所有文件 (*)"
            )
            
            if file_name:
                if not file_name.endswith('.ui'):
                    file_name += '.ui'
                
                try:
                    with open(file_name, 'w', encoding='utf-8') as f:
                        f.write(ui_code)
                    
                    self.statusBar().showMessage(f"已导出 UI 文件: {file_name}")
                
                except Exception as e:
                    QMessageBox.critical(self, "错误", f"导出代码失败: {str(e)}")
    
    def on_property_changed(self, prop_name, value):
        """处理属性变更"""
        if not self.canvas.selected_widget:
            return
        
        # 更新控件属性
        widget = self.canvas.selected_widget
        
        if prop_name == "objectName":
            widget.setObjectName(value)
        
        elif prop_name == "geometry":
            widget.setGeometry(value)
        
        elif prop_name == "text" and hasattr(widget, "setText"):
            widget.setText(value)
        
        elif prop_name == "placeholderText" and hasattr(widget, "setPlaceholderText"):
            widget.setPlaceholderText(value)
        
        elif prop_name == "checked" and hasattr(widget, "setChecked"):
            widget.setChecked(value)
        
        elif prop_name == "items":
            if hasattr(widget, "clear") and hasattr(widget, "addItems"):
                widget.clear()
                widget.addItems(value)
        
        elif prop_name == "minimum" and hasattr(widget, "setMinimum"):
            widget.setMinimum(value)
        
        elif prop_name == "maximum" and hasattr(widget, "setMaximum"):
            widget.setMaximum(value)
        
        elif prop_name == "value" and hasattr(widget, "setValue"):
            widget.setValue(value)
        
        elif prop_name == "orientation" and hasattr(widget, "setOrientation"):
            if value.lower() == "horizontal":
                widget.setOrientation(Qt.Horizontal)
            else:
                widget.setOrientation(Qt.Vertical)
        
        elif prop_name == "title" and hasattr(widget, "setTitle"):
            widget.setTitle(value)
        
        # 更新存储的属性
        for w in self.canvas.widgets:
            if w['widget'] == widget:
                if prop_name in w['properties']:
                    w['properties'][prop_name] = value
                break

# 主函数
def main():
    app = QApplication(sys.argv)
    designer = PyQtDesigner()
    designer.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
