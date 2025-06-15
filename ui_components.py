#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI Module for ExchangeUnsen Application
Generated from excel_reader.ui file
"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel,
    QLineEdit, QPushButton, QComboBox, QTableView, QMenuBar, QMenu,
    QStatusBar, QAction, QSizePolicy, QSpacerItem
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont


class ExchangeUnsenUI(QMainWindow):
    """UI Class สำหรับ ExchangeUnsen Application"""
    
    def setupUi(self):
        """ตั้งค่า UI components"""
        # Main Window properties
        self.setObjectName("MainWindow")
        self.resize(1000, 700)
        self.setWindowTitle("Excel File Reader")
        
        # Central widget
        self.centralwidget = QWidget(self)
        self.setCentralWidget(self.centralwidget)
        
        # Main vertical layout
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        
        # Top frame - File selection
        self.setup_top_frame()
        
        # Button frame - Control buttons
        self.setup_button_frame()
        
        # Status label
        self.setup_status_label()
        
        # Table view
        self.setup_table_view()
        
        # Menu bar
        self.setup_menu_bar()
        
        # Status bar
        self.statusbar = QStatusBar(self)
        self.setStatusBar(self.statusbar)
        
    def setup_top_frame(self):
        """ตั้งค่า top frame สำหรับเลือกไฟล์"""
        self.topFrame = QFrame(self.centralwidget)
        self.topFrame.setFrameShape(QFrame.StyledPanel)
        self.topFrame.setFrameShadow(QFrame.Raised)
        
        # Horizontal layout for top frame
        self.horizontalLayout = QHBoxLayout(self.topFrame)
        
        # File label
        self.fileLabel = QLabel("เลือกไฟล์ Excel:", self.topFrame)
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.fileLabel.setFont(font)
        self.horizontalLayout.addWidget(self.fileLabel)
        
        # File path line edit
        self.filePathLineEdit = QLineEdit(self.topFrame)
        self.filePathLineEdit.setReadOnly(True)
        self.filePathLineEdit.setPlaceholderText("ยังไม่ได้เลือกไฟล์")
        self.filePathLineEdit.setMinimumSize(QSize(300, 25))
        self.horizontalLayout.addWidget(self.filePathLineEdit, 1)  # stretch factor
        
        # Browse button
        self.browseButton = QPushButton("Browse...", self.topFrame)
        self.setup_browse_button_style()
        self.horizontalLayout.addWidget(self.browseButton)
        
        self.verticalLayout.addWidget(self.topFrame)
        
    def setup_browse_button_style(self):
        """ตั้งค่า style สำหรับ browse button"""
        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        self.browseButton.setFont(font)
        self.browseButton.setMinimumSize(QSize(100, 35))
        
        browse_style = """
        QPushButton {
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 8px 16px;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
        QPushButton:pressed {
            background-color: #3d8b40;
        }
        """
        self.browseButton.setStyleSheet(browse_style)
        
    def setup_button_frame(self):
        """ตั้งค่า button frame สำหรับปุ่มควบคุม"""
        self.buttonFrame = QFrame(self.centralwidget)
        self.buttonFrame.setFrameShape(QFrame.StyledPanel)
        self.buttonFrame.setFrameShadow(QFrame.Raised)
        
        # Horizontal layout for buttons
        self.buttonLayout = QHBoxLayout(self.buttonFrame)
        
        # Column label (hidden by default)
        self.columnLabel = QLabel("เชื่อมโยงโดย:", self.buttonFrame)
        font = QFont()
        font.setPointSize(9)
        font.setBold(True)
        self.columnLabel.setFont(font)
        self.columnLabel.setVisible(False)
        self.buttonLayout.addWidget(self.columnLabel)
        
        # Column combo box (hidden by default)
        self.columnComboBox = QComboBox(self.buttonFrame)
        self.setup_combo_box_style()
        self.buttonLayout.addWidget(self.columnComboBox)
        
        # Search population button (hidden by default)
        self.searchPopulationButton = QPushButton("เชื่อมโยงข้อมูล", self.buttonFrame)
        self.setup_search_button_style()
        self.buttonLayout.addWidget(self.searchPopulationButton)
        
        # Horizontal spacer
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.buttonLayout.addItem(spacer)
        
        # Clear button
        self.clearButton = QPushButton("ล้างข้อมูล", self.buttonFrame)
        self.setup_clear_button_style()
        self.buttonLayout.addWidget(self.clearButton)
        
        # Export button
        self.exportButton = QPushButton("Export", self.buttonFrame)
        self.setup_export_button_style()
        self.buttonLayout.addWidget(self.exportButton)
        
        self.verticalLayout.addWidget(self.buttonFrame)
        
    def setup_combo_box_style(self):
        """ตั้งค่า style สำหรับ combo box"""
        self.columnComboBox.setMinimumSize(QSize(150, 35))
        font = QFont()
        font.setPointSize(9)
        self.columnComboBox.setFont(font)
        self.columnComboBox.setVisible(False)
        
        combo_style = """
        QComboBox {
            background-color: white;
            border: 2px solid #DDDDDD;
            border-radius: 5px;
            padding: 5px 10px;
        }
        QComboBox:hover {
            border-color: #2196F3;
        }
        QComboBox::drop-down {
            border: none;
            background-color: #F5F5F5;
            width: 20px;
            border-top-right-radius: 3px;
            border-bottom-right-radius: 3px;
        }
        QComboBox::down-arrow {
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid #666666;
            width: 0;
            height: 0;
        }
        """
        self.columnComboBox.setStyleSheet(combo_style)
        
    def setup_search_button_style(self):
        """ตั้งค่า style สำหรับ search button"""
        font = QFont()
        font.setPointSize(9)
        font.setBold(True)
        self.searchPopulationButton.setFont(font)
        self.searchPopulationButton.setMinimumSize(QSize(150, 35))
        self.searchPopulationButton.setVisible(False)
        
        search_style = """
        QPushButton {
            background-color: #FF9800;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 8px 16px;
        }
        QPushButton:hover {
            background-color: #F57C00;
        }
        QPushButton:pressed {
            background-color: #E65100;
        }
        QPushButton:disabled {
            background-color: #CCCCCC;
            color: #666666;
        }
        """
        self.searchPopulationButton.setStyleSheet(search_style)
        
    def setup_clear_button_style(self):
        """ตั้งค่า style สำหรับ clear button"""
        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        self.clearButton.setFont(font)
        self.clearButton.setMinimumSize(QSize(100, 35))
        self.clearButton.setEnabled(False)
        
        clear_style = """
        QPushButton {
            background-color: #F44336;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 8px 16px;
        }
        QPushButton:hover {
            background-color: #D32F2F;
        }
        QPushButton:pressed {
            background-color: #B71C1C;
        }
        QPushButton:disabled {
            background-color: #CCCCCC;
            color: #666666;
        }
        """
        self.clearButton.setStyleSheet(clear_style)
        
    def setup_export_button_style(self):
        """ตั้งค่า style สำหรับ export button"""
        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        self.exportButton.setFont(font)
        self.exportButton.setMinimumSize(QSize(150, 35))
        self.exportButton.setEnabled(False)
        
        export_style = """
        QPushButton {
            background-color: #FF9800;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 8px 16px;
        }
        QPushButton:hover {
            background-color: #F57C00;
        }
        QPushButton:pressed {
            background-color: #E65100;
        }
        QPushButton:disabled {
            background-color: #CCCCCC;
            color: #666666;        }
        """
        self.exportButton.setStyleSheet(export_style)
    
    def setup_status_label(self):
        """ตั้งค่า status label และ additional info label"""
        # สร้าง horizontal layout สำหรับ status area
        self.statusLayout = QHBoxLayout()
        
        # Status label หลัก (ความกว้าง 70%)
        self.statusLabel = QLabel("สถานะ: พร้อมใช้งาน", self.centralwidget)
        font = QFont()
        font.setPointSize(10)
        self.statusLabel.setFont(font)
        
        status_style = """
        QLabel {
            color: #333333;
            padding: 5px;
            background-color: #F5F5F5;
            border: 1px solid #DDDDDD;
            border-radius: 3px;
        }
        """
        self.statusLabel.setStyleSheet(status_style)
        
        # Additional info label ใหม่ (ความกว้าง 30%)
        self.additionalInfoLabel = QLabel("", self.centralwidget)
        self.additionalInfoLabel.setFont(font)
        
        additional_style = """
        QLabel {
            color: #2E7D32;
            padding: 5px;
            background-color: #E8F5E8;
            border: 1px solid #C8E6C9;
            border-radius: 3px;
            font-weight: bold;
        }
        """
        self.additionalInfoLabel.setStyleSheet(additional_style)
          # เพิ่ม labels และ update button ลงใน horizontal layout
        self.statusLayout.addWidget(self.statusLabel, 70)  # 70% ความกว้าง
        self.statusLayout.addWidget(self.additionalInfoLabel, 25)  # 25% ความกว้าง
        
        # เพิ่ม Update button สำหรับการอัปเดท (5% ความกว้าง)
        self.updateButton = QPushButton("อัปเดท", self.centralwidget)
        self.updateButton.setFont(font)
        self.updateButton.setVisible(False)  # ซ่อนไว้ก่อน จะแสดงเมื่อมี update
        
        update_button_style = """
        QPushButton {
            color: white;
            background-color: #1976D2;
            border: 1px solid #1565C0;
            border-radius: 3px;
            padding: 5px 10px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #1565C0;
        }
        QPushButton:pressed {
            background-color: #0D47A1;
        }
        """
        self.updateButton.setStyleSheet(update_button_style)
        
        self.statusLayout.addWidget(self.updateButton, 5)  # 5% ความกว้าง
        
        # เพิ่ม horizontal layout ลงใน main vertical layout
        self.verticalLayout.addLayout(self.statusLayout)
        
    def setup_table_view(self):
        """ตั้งค่า table view"""
        self.tableView = QTableView(self.centralwidget)
        font = QFont()
        font.setPointSize(9)
        self.tableView.setFont(font)
        self.tableView.setAlternatingRowColors(True)
        self.tableView.setSelectionBehavior(QTableView.SelectRows)
        self.tableView.setSortingEnabled(True)
        
        table_style = """
        QTableView {
            gridline-color: #DDDDDD;
            background-color: white;
            selection-background-color: #E3F2FD;
        }
        QTableView::item {
            padding: 5px;
            border-bottom: 1px solid #EEEEEE;
        }
        QTableView::item:selected {
            background-color: #E3F2FD;
        }
        QHeaderView::section {
            background-color: #F5F5F5;
            padding: 8px;
            border: 1px solid #DDDDDD;
            font-weight: bold;
        }
        """
        self.tableView.setStyleSheet(table_style)
        self.verticalLayout.addWidget(self.tableView)
        
    def setup_menu_bar(self):
        """ตั้งค่า menu bar และ actions"""
        self.menubar = QMenuBar(self)
        self.menubar.setGeometry(0, 0, 1000, 26)
        self.setMenuBar(self.menubar)
        
        # File menu
        self.menuFile = QMenu("ไฟล์", self.menubar)
        self.menubar.addMenu(self.menuFile)
        
        # View menu
        self.menuView = QMenu("มุมมอง", self.menubar)
        self.menubar.addMenu(self.menuView)
        
        # Settings menu
        self.menuSettings = QMenu("ตั้งค่า", self.menubar)
        self.menubar.addMenu(self.menuSettings)
        
        # Help menu
        self.menuHelp = QMenu("ช่วยเหลือ", self.menubar)
        self.menubar.addMenu(self.menuHelp)
        
        # Actions
        self.create_actions()
        
        # Add actions to menus
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionExport)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        
        self.menuView.addAction(self.actionRefresh)
        
        self.menuSettings.addAction(self.actionMySQLSettings)
        self.menuSettings.addAction(self.actionConnectMySQL)
        self.menuSettings.addAction(self.actionDisconnectMySQL)
        
        self.menuHelp.addAction(self.actionAbout)
        
    def create_actions(self):
        """สร้าง actions สำหรับ menu"""
        # File actions
        self.actionOpen = QAction("เปิดไฟล์", self)
        self.actionOpen.setShortcut("Ctrl+O")
        
        self.actionExport = QAction("Export", self)
        self.actionExport.setShortcut("Ctrl+E")
        
        self.actionExit = QAction("ออก", self)
        self.actionExit.setShortcut("Ctrl+Q")
        
        # View actions
        self.actionRefresh = QAction("รีเฟรช", self)
        self.actionRefresh.setShortcut("F5")
        
        # Settings actions
        self.actionMySQLSettings = QAction("ตั้งค่า MySQL", self)
        self.actionMySQLSettings.setShortcut("Ctrl+M")
        
        self.actionConnectMySQL = QAction("เชื่อมต่อ MySQL", self)
        self.actionConnectMySQL.setShortcut("F6")
        
        self.actionDisconnectMySQL = QAction("ตัดการเชื่อมต่อ MySQL", self)
        self.actionDisconnectMySQL.setShortcut("F7")
        
        # Help actions
        self.actionAbout = QAction("เกี่ยวกับ", self)
