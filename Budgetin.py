import sys
import sqlite3
import csv
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QMessageBox, QLabel,
    QLineEdit, QPushButton, QSpinBox, QComboBox, QVBoxLayout, QHBoxLayout, QWidget,
    QGridLayout, QFileDialog, QDockWidget, QScrollArea, QStatusBar, QMenuBar, QAction
)
from PyQt5.QtCore import Qt

class BudgetinApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Budgetin App")
        self.setFixedSize(800, 850)

        self.current_theme = "light"

        self.setStyleSheet(self.get_stylesheet())

        self.conn = sqlite3.connect("budgetin.db")
        self.cursor = self.conn.cursor()
        self.create_table()

        self.totalBelanja = 0

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)

        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)
        theme_menu = menu_bar.addMenu("Tema")

        light_action = QAction("Light Theme", self)
        dark_action = QAction("Dark Theme", self)
        theme_menu.addAction(light_action)
        theme_menu.addAction(dark_action)

        light_action.triggered.connect(lambda: self.switch_theme("light"))
        dark_action.triggered.connect(lambda: self.switch_theme("dark"))

        title_container = QWidget()
        title_container_layout = QVBoxLayout()
        title_container_layout.setAlignment(Qt.AlignCenter)
        title_container.setLayout(title_container_layout)

        title_layout = QHBoxLayout()
        title_layout.setAlignment(Qt.AlignCenter)

        icon_label = QLabel("🛒")
        icon_label.setStyleSheet("font-size: 24px;")
        title_layout.addWidget(icon_label)

        title_label = QLabel("Budgetin")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        title_layout.addWidget(title_label)

        title_container_layout.addLayout(title_layout)

        student_label = QLabel("ATUR BELANJAAN MU DISINI")
        student_label.setStyleSheet("font-size: 12px;")
        student_label.setAlignment(Qt.AlignCenter)
        title_container_layout.addWidget(student_label)

        main_layout.addWidget(title_container)

        form_layout = QGridLayout()
        main_layout.addLayout(form_layout)

        self.BudgetlineEdit = QLineEdit()
        self.BudgetlineEdit.setPlaceholderText("Masukkan Budget")
        form_layout.addWidget(QLabel("Budget:"), 0, 0)
        form_layout.addWidget(self.BudgetlineEdit, 0, 1)

        self.NamaBarangLineEdit = QLineEdit()
        self.NamaBarangLineEdit.setPlaceholderText("Nama Barang")
        form_layout.addWidget(QLabel("Nama Barang:"), 1, 0)
        form_layout.addWidget(self.NamaBarangLineEdit, 1, 1)

        self.pasteButton = QPushButton("Paste from Clipboard")
        self.pasteButton.setStyleSheet("padding: 2px 6px;")
        self.pasteButton.clicked.connect(self.paste_from_clipboard)
        form_layout.addWidget(self.pasteButton, 1, 2)

        self.HargaLineEdit = QLineEdit()
        self.HargaLineEdit.setPlaceholderText("Harga")
        form_layout.addWidget(QLabel("Harga:"), 2, 0)
        form_layout.addWidget(self.HargaLineEdit, 2, 1)

        self.spinBoxJumlah = QSpinBox()
        self.spinBoxJumlah.setMinimum(1)
        form_layout.addWidget(QLabel("Jumlah:"), 3, 0)
        form_layout.addWidget(self.spinBoxJumlah, 3, 1)

        self.comboBoxKategori = QComboBox()
        self.comboBoxKategori.addItems(["-- Pilih --", "Makanan", "Minuman", "Elektronik", "Lainnya"])
        form_layout.addWidget(QLabel("Kategori:"), 4, 0)
        form_layout.addWidget(self.comboBoxKategori, 4, 1)

        button_layout = QHBoxLayout()
        main_layout.addLayout(button_layout)

        self.tombolTambahBarang = QPushButton("Tambah Barang")
        button_layout.addWidget(self.tombolTambahBarang)

        self.tombolReset = QPushButton("Reset")
        button_layout.addWidget(self.tombolReset)

        self.tombolSimpan = QPushButton("Export CSV")
        button_layout.addWidget(self.tombolSimpan)

        self.dockWidget = QDockWidget("Search", self)
        self.dockWidget.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        search_widget = QWidget()
        search_layout = QHBoxLayout()
        search_widget.setLayout(search_layout)
        self.lineEditSearch = QLineEdit()
        self.lineEditSearch.setPlaceholderText("Cari berdasarkan nama...")
        search_layout.addWidget(self.lineEditSearch)
        self.dockWidget.setWidget(search_widget)
        self.addDockWidget(Qt.TopDockWidgetArea, self.dockWidget)
        self.lineEditSearch.textChanged.connect(self.search_items)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        self.tableWidget = QTableWidget()
        self.tableWidget.setColumnCount(6)
        self.tableWidget.setHorizontalHeaderLabels(["Nama", "Harga", "Jumlah", "Subtotal", "Kategori", ""])
        self.tableWidget.setSelectionMode(QTableWidget.SingleSelection)
        self.tableWidget.setSelectionBehavior(QTableWidget.SelectRows)
        self.tableWidget.setColumnWidth(0, 200)
        self.tableWidget.setColumnWidth(1, 110)
        self.tableWidget.setColumnWidth(2, 110)
        self.tableWidget.setColumnWidth(3, 110)
        self.tableWidget.setColumnWidth(4, 130)
        self.tableWidget.setColumnWidth(5, 90)
        scroll_area.setWidget(self.tableWidget)
        main_layout.addWidget(scroll_area)

        total_layout = QHBoxLayout()
        main_layout.addLayout(total_layout)
        total_layout.addWidget(QLabel("Total:"))
        self.LabelTotal = QLabel("0")
        total_layout.addWidget(self.LabelTotal)
        total_layout.addWidget(QLabel("Sisa:"))
        self.LabelSisa = QLabel("0")
        total_layout.addWidget(self.LabelSisa)

        self.statusBar = QStatusBar()
        status_label = QLabel("LALU MUHAMMAD NOVAL ADIPRATAMA | F1D022956")
        status_label.setAlignment(Qt.AlignCenter)
        self.statusBar.addWidget(status_label, 1)
        self.setStatusBar(self.statusBar)

        self.tombolTambahBarang.clicked.connect(self.tambahBarang)
        self.tombolReset.clicked.connect(self.resetData)
        self.tombolSimpan.clicked.connect(self.export_to_csv)
        self.tableWidget.itemClicked.connect(self.edit_item)

        self.load_data()

    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS items (
                nama TEXT NOT NULL,
                harga INTEGER NOT NULL,
                jumlah INTEGER NOT NULL,
                subtotal INTEGER NOT NULL,
                kategori TEXT NOT NULL
            )
        """)
        self.conn.commit()

    def tambahBarang(self):
        nama = self.NamaBarangLineEdit.text()
        harga_text = self.HargaLineEdit.text()
        jumlah = self.spinBoxJumlah.value()
        kategori = self.comboBoxKategori.currentText()

        if not nama or not harga_text or kategori == "-- Pilih --":
            QMessageBox.warning(self, "Input Tidak Lengkap", "Harap isi semua field.")
            return

        try:
            harga = int(harga_text)
        except ValueError:
            QMessageBox.warning(self, "Input Salah", "Harga harus berupa angka.")
            return

        subtotal = harga * jumlah

        try:
            budget = int(self.BudgetlineEdit.text())
        except ValueError:
            QMessageBox.warning(self, "Input Salah", "Budget harus diisi dan berupa angka.")
            return

        if self.totalBelanja + subtotal > budget:
            QMessageBox.warning(self, "Melebihi Budget", "Total belanja melebihi budget!")
            return

        self.cursor.execute("""
            INSERT INTO items (nama, harga, jumlah, subtotal, kategori)
            VALUES (?, ?, ?, ?, ?)
        """, (nama, harga, jumlah, subtotal, kategori))
        self.conn.commit()

        self.totalBelanja += subtotal
        self.LabelTotal.setText(str(self.totalBelanja))
        self.hitungSisa()

        self.NamaBarangLineEdit.clear()
        self.HargaLineEdit.clear()
        self.spinBoxJumlah.setValue(1)
        self.comboBoxKategori.setCurrentIndex(0)

        self.load_data()

    def load_data(self, search_text=""):
        self.tableWidget.setRowCount(0)
        query = "SELECT nama, harga, jumlah, subtotal, kategori FROM items"
        if search_text:
            query += " WHERE nama LIKE ?"
            self.cursor.execute(query, (f"%{search_text}%",))
        else:
            self.cursor.execute(query)
        
        for row_data in self.cursor.fetchall():
            row = self.tableWidget.rowCount()
            self.tableWidget.insertRow(row)
            for col, data in enumerate(row_data):
                self.tableWidget.setItem(row, col, QTableWidgetItem(str(data)))

            delete_button = QPushButton("Delete")
            delete_button.clicked.connect(lambda _, r=row: self.delete_item(r))
            self.tableWidget.setCellWidget(row, 5, delete_button)
        
        self.calculate_total()

    def calculate_total(self):
        self.totalBelanja = 0
        self.cursor.execute("SELECT SUM(subtotal) FROM items")
        result = self.cursor.fetchone()[0]
        self.totalBelanja = result if result else 0
        self.LabelTotal.setText(str(self.totalBelanja))
        self.hitungSisa()

    def hitungSisa(self):
        try:
            budget = int(self.BudgetlineEdit.text())
        except ValueError:
            self.LabelSisa.setText("Isi Budget")
            return
        sisa = budget - self.totalBelanja
        self.LabelSisa.setText(str(sisa))

    def resetData(self):
        self.BudgetlineEdit.clear()
        self.NamaBarangLineEdit.clear()
        self.HargaLineEdit.clear()
        self.spinBoxJumlah.setValue(1)
        self.comboBoxKategori.setCurrentIndex(0)
        self.LabelTotal.clear()
        self.LabelSisa.clear()
        self.lineEditSearch.clear()
        self.tombolTambahBarang.setText("Tambah Barang")
        self.tombolTambahBarang.disconnect()
        self.tombolTambahBarang.clicked.connect(self.tambahBarang)
        self.cursor.execute("DELETE FROM items")
        self.conn.commit()
        self.tableWidget.setRowCount(0)
        self.totalBelanja = 0

    def search_items(self):
        search_text = self.lineEditSearch.text()
        self.load_data(search_text)

    def edit_item(self, item):
        row = item.row()
        nama = self.tableWidget.item(row, 0).text()
        harga = self.tableWidget.item(row, 1).text()
        jumlah = self.tableWidget.item(row, 2).text()
        kategori = self.tableWidget.item(row, 4).text()

        self.NamaBarangLineEdit.setText(nama)
        self.HargaLineEdit.setText(harga)
        self.spinBoxJumlah.setValue(int(jumlah))
        self.comboBoxKategori.setCurrentText(kategori)

        self.original_data = (nama, int(harga), int(jumlah), int(self.tableWidget.item(row, 3).text()), kategori)

        self.tombolTambahBarang.setText("Update")
        self.tombolTambahBarang.disconnect()
        self.tombolTambahBarang.clicked.connect(self.update_item)

        def reset_button():
            if (not self.NamaBarangLineEdit.text() and
                not self.HargaLineEdit.text() and
                self.spinBoxJumlah.value() == 1 and
                self.comboBoxKategori.currentText() == "-- Pilih --"):
                self.tombolTambahBarang.setText("Tambah Barang")
                self.tombolTambahBarang.disconnect()
                self.tombolTambahBarang.clicked.connect(self.tambahBarang)

        self.NamaBarangLineEdit.textChanged.connect(reset_button)
        self.HargaLineEdit.textChanged.connect(reset_button)
        self.spinBoxJumlah.valueChanged.connect(reset_button)
        self.comboBoxKategori.currentIndexChanged.connect(reset_button)

    def update_item(self):
        new_nama = self.NamaBarangLineEdit.text()
        new_harga_text = self.HargaLineEdit.text()
        new_jumlah = self.spinBoxJumlah.value()
        new_kategori = self.comboBoxKategori.currentText()

        if not new_nama or not new_harga_text or new_kategori == "-- Pilih --":
            QMessageBox.warning(self, "Input Tidak Lengkap", "Harap isi semua field.")
            return

        try:
            new_harga = int(new_harga_text)
        except ValueError:
            QMessageBox.warning(self, "Input Salah", "Harga harus berupa angka.")
            return

        new_subtotal = new_harga * new_jumlah
        old_nama, old_harga, old_jumlah, old_subtotal, old_kategori = self.original_data

        try:
            budget = int(self.BudgetlineEdit.text())
        except ValueError:
            QMessageBox.warning(self, "Input Salah", "Budget harus diisi dan berupa angka.")
            return

        if self.totalBelanja - old_subtotal + new_subtotal > budget:
            QMessageBox.warning(self, "Melebihi Budget", "Total belanja melebihi budget!")
            return

        self.cursor.execute("""
            UPDATE items
            SET nama = ?, harga = ?, jumlah = ?, subtotal = ?, kategori = ?
            WHERE nama = ? AND harga = ? AND jumlah = ? AND subtotal = ? AND kategori = ?
        """, (new_nama, new_harga, new_jumlah, new_subtotal, new_kategori,
              old_nama, old_harga, old_jumlah, old_subtotal, old_kategori))
        self.conn.commit()

        self.NamaBarangLineEdit.clear()
        self.HargaLineEdit.clear()
        self.spinBoxJumlah.setValue(1)
        self.comboBoxKategori.setCurrentIndex(0)
        self.tombolTambahBarang.setText("Tambah Barang")
        self.tombolTambahBarang.disconnect()
        self.tombolTambahBarang.clicked.connect(self.tambahBarang)

        self.load_data()

    def delete_item(self, row):
        nama = self.tableWidget.item(row, 0).text()
        harga = int(self.tableWidget.item(row, 1).text())
        jumlah = int(self.tableWidget.item(row, 2).text())
        subtotal = int(self.tableWidget.item(row, 3).text())
        kategori = self.tableWidget.item(row, 4).text()

        self.cursor.execute("""
            DELETE FROM items
            WHERE nama = ? AND harga = ? AND jumlah = ? AND subtotal = ? AND kategori = ?
        """, (nama, harga, jumlah, subtotal, kategori))
        self.conn.commit()
        self.load_data()

    def export_to_csv(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save CSV File",
            "daftar_belanja.csv",
            "CSV Files (*.csv)"
        )

        if not file_path:
            return

        try:
            with open(file_path, "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["Nama", "Harga", "Jumlah", "Subtotal", "Kategori"])
                self.cursor.execute("SELECT nama, harga, jumlah, subtotal, kategori FROM items")
                for row in self.cursor.fetchall():
                    writer.writerow(row)
            QMessageBox.information(self, "Berhasil", f"Data berhasil diekspor ke {file_path}.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal mengekspor data: {str(e)}")

    def paste_from_clipboard(self):
        clipboard_text = QApplication.clipboard().text().strip()
        if clipboard_text:
            self.NamaBarangLineEdit.setText(clipboard_text)
        else:
            QMessageBox.warning(self, "Clipboard Kosong", "Tidak ada teks di clipboard.")

    def switch_theme(self, theme):
        self.current_theme = theme
        self.setStyleSheet(self.get_stylesheet())

    def get_stylesheet(self):
        if self.current_theme == "light":
            return """
                QWidget {
                    background-color: #fff;
                }
                QPushButton {
                    background-color: #FFA500;
                    color: #fff;
                    border-radius: 8px;
                    padding: 6px 12px;
                }
                QPushButton:hover {
                    background-color: #e69500;
                }
                QTableWidget {
                    background-color: #fff;
                    gridline-color: #FFA500;
                    border: 1px solid #FFA500;
                }
                QHeaderView::section {
                    background-color: #FFA500;
                    color: white;
                    padding: 4px;
                    border: 1px solid #ddd;
                }
                QLabel {
                    color: #000;
                }
            """
        else:
            return """
                QWidget {
                    background-color: #2c2c2c;
                }
                QPushButton {
                    background-color: #ff8c00;
                    color: #fff;
                    border-radius: 8px;
                    padding: 6px 12px;
                }
                QPushButton:hover {
                    background-color: #e07b00;
                }
                QTableWidget {
                    background-color: #3c3c3c;
                    gridline-color: #ff8c00;
                    border: 1px solid #ff8c00;
                    color: #fff;
                }
                QHeaderView::section {
                    background-color: #ff8c00;
                    color: white;
                    padding: 4px;
                    border: 1px solid #555;
                }
                QLabel {
                    color: #fff;
                }
                QLineEdit {
                    background-color: #444;
                    color: #fff;
                    border: 1px solid #666;
                }
                QSpinBox {
                    background-color: #444;
                    color: #fff;
                    border: 1px solid #666;
                }
                QComboBox {
                    background-color: #444;
                    color: #fff;
                    border: 1px solid #666;
                }
                QComboBox QAbstractItemView {
                    background-color: #444;
                    color: #fff;
                    selection-background-color: #555;
                }
            """

    def closeEvent(self, event):
        self.conn.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BudgetinApp()
    window.show()
    sys.exit(app.exec_())