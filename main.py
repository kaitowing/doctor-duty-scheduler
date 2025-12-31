import sys
import json
import os
from datetime import datetime, date
from calendar import monthrange, day_name
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
                             QComboBox, QLabel, QMessageBox, QDialog, QListWidget,
                             QFileDialog, QHeaderView, QSpinBox)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QColor, QFont, QPainter, QPageSize
from PyQt6.QtPrintSupport import QPrinter
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_CENTER
from PIL import Image, ImageDraw, ImageFont


class HistoryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Histórico de Escalas")
        self.setMinimumSize(500, 400)
        self.selected_file = None
        
        layout = QVBoxLayout()
        
        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self.on_item_double_clicked)
        layout.addWidget(QLabel("Escalas Salvas:"))
        layout.addWidget(self.list_widget)
        
        btn_layout = QHBoxLayout()
        load_btn = QPushButton("Carregar Selecionada")
        load_btn.clicked.connect(self.accept)
        delete_btn = QPushButton("Excluir")
        delete_btn.clicked.connect(self.delete_selected)
        close_btn = QPushButton("Fechar")
        close_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(load_btn)
        btn_layout.addWidget(delete_btn)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        self.load_history()
    
    def load_history(self):
        self.list_widget.clear()
        escalas_dir = Path("escalas")
        if escalas_dir.exists():
            files = sorted(escalas_dir.glob("*.json"), reverse=True)
            for file in files:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    mes = data.get('mes', '')
                    ano = data.get('ano', '')
                    item_text = f"{mes}/{ano} - {file.stem}"
                    self.list_widget.addItem(item_text)
    
    def on_item_double_clicked(self, item):
        self.accept()
    
    def delete_selected(self):
        current_item = self.list_widget.currentItem()
        if current_item:
            reply = QMessageBox.question(self, 'Confirmar Exclusão', 
                                        'Deseja realmente excluir esta escala?',
                                        QMessageBox.StandardButton.Yes | 
                                        QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                item_text = current_item.text()
                file_name = item_text.split(" - ")[1] + ".json"
                file_path = Path("escalas") / file_name
                if file_path.exists():
                    file_path.unlink()
                    self.load_history()
    
    def get_selected_file(self):
        current_item = self.list_widget.currentItem()
        if current_item:
            item_text = current_item.text()
            file_name = item_text.split(" - ")[1] + ".json"
            return Path("escalas") / file_name
        return None


class PlantaoApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Escalas de Plantão")
        self.setMinimumSize(1200, 700)
        
        self.meses = {
            1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
            5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
            9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
        }
        
        self.dias_semana = {
            0: "Segunda", 1: "Terça", 2: "Quarta", 3: "Quinta",
            4: "Sexta", 5: "Sábado", 6: "Domingo"
        }
        
        Path("escalas").mkdir(exist_ok=True)
        
        self.init_ui()
        
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        title_label = QLabel("Sistema de Escalas de Plantão Hospitalar")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)
        
        controls_layout.addWidget(QLabel("Mês:"))
        self.mes_combo = QComboBox()
        for num, nome in self.meses.items():
            self.mes_combo.addItem(nome, num)
        current_month = datetime.now().month
        self.mes_combo.setCurrentIndex(current_month - 1)
        controls_layout.addWidget(self.mes_combo)
        
        controls_layout.addWidget(QLabel("Ano:"))
        self.ano_spin = QSpinBox()
        self.ano_spin.setRange(2020, 2050)
        self.ano_spin.setValue(datetime.now().year)
        controls_layout.addWidget(self.ano_spin)
        
        gerar_btn = QPushButton("Gerar Tabela")
        gerar_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px 20px;
                font-size: 14px;
                font-weight: bold;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        gerar_btn.clicked.connect(self.gerar_tabela)
        controls_layout.addWidget(gerar_btn)
        
        controls_layout.addStretch()
        
        historico_btn = QPushButton("Histórico")
        historico_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 8px 20px;
                font-size: 14px;
                font-weight: bold;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
        """)
        historico_btn.clicked.connect(self.abrir_historico)
        controls_layout.addWidget(historico_btn)
        
        main_layout.addLayout(controls_layout)
        
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Data", "Dia da Semana", "Noite", "Tarde", "Manhã"])
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                gridline-color: #d0d0d0;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #5c6bc0;
                color: white;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                border: 1px solid #4a5a9f;
            }
        """)
        
        main_layout.addWidget(self.table)
        
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        salvar_btn = QPushButton("Salvar Escala")
        salvar_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                padding: 10px 25px;
                font-size: 14px;
                font-weight: bold;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #e68900;
            }
        """)
        salvar_btn.clicked.connect(self.salvar_escala)
        buttons_layout.addWidget(salvar_btn)
        
        pdf_btn = QPushButton("Exportar PDF")
        pdf_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 10px 25px;
                font-size: 14px;
                font-weight: bold;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        pdf_btn.clicked.connect(self.exportar_pdf)
        buttons_layout.addWidget(pdf_btn)
        
        png_btn = QPushButton("Exportar PNG")
        png_btn.setStyleSheet("""
            QPushButton {
                background-color: #9C27B0;
                color: white;
                padding: 10px 25px;
                font-size: 14px;
                font-weight: bold;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #7b1fa2;
            }
        """)
        png_btn.clicked.connect(self.exportar_png)
        buttons_layout.addWidget(png_btn)
        
        main_layout.addLayout(buttons_layout)
        
        self.gerar_tabela()
    
    def gerar_tabela(self):
        mes = self.mes_combo.currentData()
        ano = self.ano_spin.value()
        
        num_dias = monthrange(ano, mes)[1]
        self.table.setRowCount(num_dias)
        
        for dia in range(1, num_dias + 1):
            data_obj = date(ano, mes, dia)
            dia_semana = data_obj.weekday()
            
            item_data = QTableWidgetItem(f"{dia:02d}/{mes:02d}/{ano}")
            item_data.setFlags(item_data.flags() & ~Qt.ItemFlag.ItemIsEditable)
            item_dia = QTableWidgetItem(self.dias_semana[dia_semana])
            item_data.setFlags(item_data.flags() & ~Qt.ItemFlag.ItemIsEditable)
            item_dia.setFlags(item_dia.flags() & ~Qt.ItemFlag.ItemIsEditable)
            item_data.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_dia.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            is_weekend = dia_semana in [4, 5, 6]
            
            if is_weekend:
                cor_fundo = QColor(138, 180, 248)
                item_data.setBackground(cor_fundo)
                item_dia.setBackground(cor_fundo)
                item_data.setForeground(QColor(Qt.GlobalColor.black))
                item_dia.setForeground(QColor(Qt.GlobalColor.black))

            self.table.setItem(dia - 1, 0, item_data)
            self.table.setItem(dia - 1, 1, item_dia)
            
            item_noite = QTableWidgetItem("")
            item_tarde = QTableWidgetItem("")
            item_manha = QTableWidgetItem("")

            for cell in (item_noite, item_tarde, item_manha):
                cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            if is_weekend:
                for cell in (item_noite, item_tarde, item_manha):
                    cell.setBackground(cor_fundo)
                    cell.setForeground(QColor(Qt.GlobalColor.black))

            self.table.setItem(dia - 1, 2, item_noite)
            self.table.setItem(dia - 1, 3, item_tarde)
            self.table.setItem(dia - 1, 4, item_manha)
    
    def salvar_escala(self):
        mes = self.mes_combo.currentData()
        ano = self.ano_spin.value()
        
        data = {
            'mes': mes,
            'ano': ano,
            'escalas': []
        }
        
        for row in range(self.table.rowCount()):
            data_item = self.table.item(row, 0)
            dia_item = self.table.item(row, 1)
            noite_item = self.table.item(row, 2)
            tarde_item = self.table.item(row, 3)
            manha_item = self.table.item(row, 4)
            
            data['escalas'].append({
                'data': data_item.text() if data_item else '',
                'dia_semana': dia_item.text() if dia_item else '',
                'noite': noite_item.text() if noite_item else '',
                'tarde': tarde_item.text() if tarde_item else '',
                'manha': manha_item.text() if manha_item else ''
            })
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"escalas/escala_{mes:02d}_{ano}_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        QMessageBox.information(self, "Sucesso", "Escala salva com sucesso!")
    
    def abrir_historico(self):
        dialog = HistoryDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            file_path = dialog.get_selected_file()
            if file_path and file_path.exists():
                self.carregar_escala(file_path)
    
    def carregar_escala(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        mes = data['mes']
        ano = data['ano']
        
        self.mes_combo.setCurrentIndex(mes - 1)
        self.ano_spin.setValue(ano)
        
        self.gerar_tabela()
        
        for row, escala in enumerate(data['escalas']):
            if row < self.table.rowCount():
                self.table.item(row, 2).setText(escala.get('noite', ''))
                self.table.item(row, 3).setText(escala.get('tarde', ''))
                self.table.item(row, 4).setText(escala.get('manha', ''))
        
        QMessageBox.information(self, "Sucesso", "Escala carregada com sucesso!")
    
    def exportar_pdf(self):
        if self.table.rowCount() == 0:
            QMessageBox.warning(self, "Aviso", "Gere uma tabela primeiro!")
            return
        
        mes = self.mes_combo.currentData()
        ano = self.ano_spin.value()
        mes_nome = self.meses[mes]
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Salvar PDF", 
            f"Escala_{mes_nome}_{ano}.pdf",
            "PDF Files (*.pdf)"
        )
        
        if not filename:
            return
        
        doc = SimpleDocTemplate(filename, pagesize=landscape(A4),
                               leftMargin=15*mm, rightMargin=15*mm,
                               topMargin=15*mm, bottomMargin=15*mm)
        
        elements = []
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#1a237e'),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        title = Paragraph(f"Escala de Plantão - {mes_nome}/{ano}", title_style)
        elements.append(title)
        elements.append(Spacer(1, 10*mm))
        
        table_data = [['Data', 'Dia da Semana', 'Noite', 'Tarde', 'Manhã']]
        
        for row in range(self.table.rowCount()):
            row_data = []
            for col in range(5):
                item = self.table.item(row, col)
                row_data.append(item.text() if item else '')
            table_data.append(row_data)
        
        table = Table(table_data, colWidths=[35*mm, 40*mm, 60*mm, 60*mm, 60*mm])
        
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#5c6bc0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ])
        
        for row in range(1, len(table_data)):
            dia_semana = table_data[row][1]
            if dia_semana in ['Sexta', 'Sábado', 'Domingo']:
                style.add('BACKGROUND', (0, row), (-1, row), colors.HexColor('#8AB4F8'))
        
        table.setStyle(style)
        elements.append(table)
        
        doc.build(elements)
        
        QMessageBox.information(self, "Sucesso", f"PDF exportado com sucesso!\n{filename}")
    
    def exportar_png(self):
        if self.table.rowCount() == 0:
            QMessageBox.warning(self, "Aviso", "Gere uma tabela primeiro!")
            return
        
        mes = self.mes_combo.currentData()
        ano = self.ano_spin.value()
        mes_nome = self.meses[mes]
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Salvar PNG", 
            f"Escala_{mes_nome}_{ano}.png",
            "PNG Files (*.png)"
        )
        
        if not filename:
            return
        
        row_height = 35
        header_height = 50
        title_height = 60
        margin = 30
        
        col_widths = [120, 140, 220, 220, 220]
        width = sum(col_widths) + 2 * margin
        height = title_height + header_height + (self.table.rowCount() * row_height) + 2 * margin
        
        img = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(img)
        
        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
            header_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
            cell_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
        except:
            title_font = ImageFont.load_default()
            header_font = ImageFont.load_default()
            cell_font = ImageFont.load_default()
        
        title_text = f"Escala de Plantão - {mes_nome}/{ano}"
        title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        draw.text(((width - title_width) // 2, margin), title_text, 
                 fill='#1a237e', font=title_font)
        
        headers = ['Data', 'Dia da Semana', 'Noite', 'Tarde', 'Manhã']
        y = margin + title_height
        x = margin
        
        for i, header in enumerate(headers):
            draw.rectangle([x, y, x + col_widths[i], y + header_height], 
                          fill='#5c6bc0', outline='#4a5a9f', width=2)
            
            text_bbox = draw.textbbox((0, 0), header, font=header_font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            text_x = x + (col_widths[i] - text_width) // 2
            text_y = y + (header_height - text_height) // 2
            draw.text((text_x, text_y), header, fill='white', font=header_font)
            
            x += col_widths[i]
        
        y += header_height
        
        for row in range(self.table.rowCount()):
            x = margin
            
            dia_semana = self.table.item(row, 1).text() if self.table.item(row, 1) else ''
            is_weekend = dia_semana in ['Sexta', 'Sábado', 'Domingo']
            bg_color = '#8AB4F8' if is_weekend else ('#f5f5f5' if row % 2 == 0 else 'white')
            
            for col in range(5):
                item = self.table.item(row, col)
                text = item.text() if item else ''
                
                draw.rectangle([x, y, x + col_widths[col], y + row_height], 
                              fill=bg_color, outline='#d0d0d0', width=1)
                
                if text:
                    text_bbox = draw.textbbox((0, 0), text, font=cell_font)
                    text_width = text_bbox[2] - text_bbox[0]
                    text_height = text_bbox[3] - text_bbox[1]
                    
                    text_x = x + (col_widths[col] - text_width) // 2
                    text_y = y + (row_height - text_height) // 2
                    draw.text((text_x, text_y), text, fill='black', font=cell_font)
                
                x += col_widths[col]
            
            y += row_height
        
        img.save(filename, 'PNG')
        
        QMessageBox.information(self, "Sucesso", f"PNG exportado com sucesso!\n{filename}")


def main():
    app = QApplication(sys.argv)
    
    app.setStyle('Fusion')
    
    window = PlantaoApp()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
