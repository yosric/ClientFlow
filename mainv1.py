import ctypes
import os
import tempfile
import sys
import time
from PySide6.QtWidgets import (
        QApplication, QWidget, QVBoxLayout, QHBoxLayout,
        QPushButton, QTableWidget, QTableWidgetItem,
        QLineEdit, QMessageBox, QInputDialog, QDateEdit,
        QLabel, QFileDialog, QDialog, QFormLayout, QDialogButtonBox,
    )


from PySide6.QtGui import QIcon, QImage
from PySide6.QtCore import QDate, Qt
from database import init_db, get_connection, reset_db
from datetime import date, datetime
from PySide6.QtWidgets import QSplashScreen
from PySide6.QtGui import QPixmap
import resources_rc
from PySide6.QtCore import Qt

# ReportLab imports for PDF generation
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle,
    Paragraph, Spacer
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
import os



def generate_reference():
        """Génère une référence automatique unique pour les ventes"""
        from datetime import datetime
        timestamp = datetime.now().strftime('%y%m%d')
        # Numéro aléatoire plus court
        import random
        random_num = random.randint(1000, 9999)
        return f"V{timestamp}{random_num}"


def export_table_to_pdf(table, filename, title, client_info=None, exclude_columns=None):
    """
    Export table to PDF using ReportLab
    exclude_columns: list of column indices to exclude from export
    """
    if exclude_columns is None:
        exclude_columns = []

    # Get ReportLab styles
    styles = getSampleStyleSheet()

    # Extract table data
    rows = table.rowCount()
    cols = table.columnCount()
    export_cols = [col for col in range(cols) if col not in exclude_columns]

    table_data = []

    # Add headers
    header_row = []
    for col in export_cols:
        header_item = table.horizontalHeaderItem(col)
        if header_item:
            header_row.append(header_item.text())
        else:
            header_row.append(f"Column {col+1}")
    table_data.append(header_row)

    # Add data rows
    for row in range(rows):
        data_row = []
        for col in export_cols:
            item = table.item(row, col)
            if item:
                text = item.text()
                # Let generate_pdf_with_data handle text wrapping
                data_row.append(text)
            else:
                # Handle widgets
                widget = table.cellWidget(row, col)
                if widget and isinstance(widget, QPushButton):
                    data_row.append(widget.text())
                else:
                    data_row.append("")
        table_data.append(data_row)

    # Add totals row if there are numeric columns
    if rows > 0:
        totals_row = ["Total"]
        has_totals = False
        for col_idx, col in enumerate(export_cols):
            if col_idx == 0:  # Skip first column (usually description/name)
                continue
            
            # Skip phone number columns
            header_item = table.horizontalHeaderItem(col)
            if header_item:
                header_text = header_item.text().lower()
                if 'téléphone' in header_text or 'tel' in header_text or 'phone' in header_text:
                    totals_row.append("")
                    continue
            
            total = 0
            count = 0
            for row in range(rows):
                item = table.item(row, col)
                if item:
                    text = item.text()
                    # Try to extract numeric value
                    try:
                        # Remove currency symbols and spaces
                        clean_text = text.replace('DT', '').replace('DT', '').replace(' ', '').replace(',', '.')
                        value = float(clean_text)
                        total += value
                        count += 1
                    except (ValueError, AttributeError):
                        pass
            if count > 0:
                totals_row.append(f"{total:.3f} DT")
                has_totals = True
            else:
                totals_row.append("")

        if has_totals:
            table_data.append(totals_row)

    # Generate PDF
    generate_pdf_with_data(filename, table_data, title, client_info)


def generate_pdf_with_data(filename, table_data, title, client_info=None):
    """
    Generate a professional commercial report PDF with improved design
    """
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=6 * cm,  # Reduced from 7.5cm
        bottomMargin=3 * cm
    )

    styles = getSampleStyleSheet()
    elements = []

    # =============================================
    # CUSTOM STYLES
    # =============================================

    # Professional title style
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=18,  # Made smaller from 24
        textColor=colors.HexColor("#1F2A44"),
        spaceAfter=20,
        alignment=TA_LEFT,  # Changed from TA_CENTER to TA_LEFT
        fontName='Helvetica-Bold'
    )

    # Cell text style for wrapping
    cell_style = ParagraphStyle(
        'CellStyle',
        parent=styles['Normal'],
        fontSize=10,
        leading=12,
        alignment=TA_LEFT
    )

    cell_style_center = ParagraphStyle(
        'CellStyleCenter',
        parent=styles['Normal'],
        fontSize=10,
        leading=12,
        alignment=TA_CENTER
    )

    # =============================================
    # TITLE SECTION WITH BULLET POINT
    # =============================================
    # Add bullet point to title
    bullet_title = f"📄 {title}"
    title_para = Paragraph(bullet_title, title_style)
    elements.append(title_para)
    elements.append(Spacer(1, 0.5 * cm))

    # Client info with structured bullet points
    if client_info:
        # Parse client info and create structured display
        info_parts = client_info.split(' | ')
        if len(info_parts) >= 4:
            client_name = info_parts[0].replace('Client: ', '')
            description = info_parts[1].replace('Description: ', '')
            total_amount = info_parts[2].replace('Montant Total: ', '')
            remaining_amount = info_parts[3].replace('Reste à payer: ', '')

            # Create a professional info box
            # Info box data
            info_data = [
                ['👤 Client:', client_name],
                ['📦 Description:', description],
                ['💰 Montant Total:', total_amount],
                ['💳 Reste à payer:', remaining_amount]
            ]

            # Create info table with box styling
            info_table = Table(info_data, colWidths=[3.5 * cm, 12 * cm])

            info_table.setStyle(TableStyle([
                # Header styling (first column)
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor("#F7FAFC")),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (0, -1), 10),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor("#1F2A44")),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

                # Data styling (second column)
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (1, 0), (1, -1), 10),
                ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor("#2D3748")),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('VALIGN', (1, 0), (1, -1), 'MIDDLE'),

                # Box styling
                ('BOX', (0, 0), (-1, -1), 1.5, colors.HexColor("#1F2A44")),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('LEFTPADDING', (0, 0), (-1, -1), 12),
                ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ]))

            elements.append(info_table)
            elements.append(Spacer(1, 0.5 * cm))
        elif len(info_parts) >= 3:
            # Fallback for older format without remaining amount
            client_name = info_parts[0].replace('Client: ', '')
            description = info_parts[1].replace('Description: ', '')
            total_amount = info_parts[2].replace('Montant Total: ', '')

            # Create a professional info box
            # Info box data
            info_data = [
                ['👤 Client:', client_name],
                ['📦 Description:', description],
                ['💰 Montant Total:', total_amount]
            ]

            # Create info table with box styling
            info_table = Table(info_data, colWidths=[3.5 * cm, 12 * cm])

            info_table.setStyle(TableStyle([
                # Header styling (first column)
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor("#F7FAFC")),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (0, -1), 10),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor("#1F2A44")),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

                # Data styling (second column)
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (1, 0), (1, -1), 10),
                ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor("#2D3748")),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('VALIGN', (1, 0), (1, -1), 'MIDDLE'),

                # Box styling
                ('BOX', (0, 0), (-1, -1), 1.5, colors.HexColor("#1F2A44")),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('LEFTPADDING', (0, 0), (-1, -1), 12),
                ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ]))

            elements.append(info_table)
            elements.append(Spacer(1, 0.5 * cm))
        else:
            # Fallback for other formats
            client_style = ParagraphStyle(
                'ClientStyle',
                parent=styles['Normal'],
                fontSize=12,
                textColor=colors.HexColor("#1F2A44"),
                spaceAfter=10,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            )
            client_para = Paragraph(f"📋 {client_info}", client_style)
            elements.append(client_para)
            elements.append(Spacer(1, 0.3 * cm))

    # =============================================
    # PROFESSIONAL TABLE WITH TEXT WRAPPING
    # =============================================

    # Wrap text in cells to prevent overflow
    wrapped_data = []
    for row_idx, row in enumerate(table_data):
        wrapped_row = []
        for col_idx, cell in enumerate(row):
            if row_idx == 0:  # Header row - keep as is
                wrapped_row.append(cell)
            else:  # Data rows - wrap text
                # First column left-aligned, others centered
                style = cell_style if col_idx == 0 else cell_style_center
                wrapped_row.append(Paragraph(str(cell), style))
        wrapped_data.append(wrapped_row)

    # Calculate column widths based on number of columns and content type
    num_cols = len(table_data[0]) if table_data else 4

    # Determine column widths based on content type
    if num_cols == 7:  # History format (Date, Amount, Mode, Note, Client, Description, Total)
        col_widths = [2 * cm, 2 * cm, 1.8 * cm, 2.5 * cm, 2.5 * cm, 3 * cm, 2 * cm]
    elif num_cols == 6:
        # Client list format with "Téléphone" header
        if any("Téléphone" in str(h) or "Tél" in str(h) for h in table_data[0]):
            # Slightly narrower table for nicer left/right margins in PDF
            col_widths = [3 * cm, 3 * cm, 3.5 * cm, 3.5 * cm, 3 * cm, 3 * cm]
        else:  # Sales format with client info
            col_widths = [2.5 * cm, 3 * cm, 3 * cm, 3 * cm, 3 * cm, 2.5 * cm]
    elif num_cols == 5:  # Client list format (Name, Phone, Address, Email, Credit)
        col_widths = [3.5 * cm, 3 * cm, 5 * cm, 4.5 * cm, 3 * cm]
    elif num_cols == 4:  # Standard format or History (Date, Amount, Mode, Note)
        col_widths = [3 * cm, 3 * cm, 3.5 * cm, 6 * cm]  # Optimized for history format
    else:
        # Auto-calculate for other formats
        total_width = A4[0] - 4 * cm  # Account for margins
        col_widths = [total_width / num_cols] * num_cols

    table = Table(wrapped_data, repeatRows=1, colWidths=col_widths)
    # Center the client list table to preserve margins
    if num_cols == 6 and any("Téléphone" in str(h) or "Tél" in str(h) for h in table_data[0]):
        table.hAlign = "CENTER"

    # Enhanced table styling
    table.setStyle(TableStyle([
        # Header styling
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1F2A44")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),  # Reduced from 11 to prevent overflow
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),  # Reduced from 12
        ('TOPPADDING', (0, 0), (-1, 0), 8),  # Reduced from 12

        # Data rows styling
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),  # First column left-aligned
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),  # Other columns centered
        ('VALIGN', (0, 1), (-1, -1), 'TOP'),  # Changed to TOP for wrapped text
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('LEFTPADDING', (0, 1), (-1, -1), 10),
        ('RIGHTPADDING', (0, 1), (-1, -1), 10),

        # Alternating row colors for readability
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F7FA")]),

        # Grid lines
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E0E0E0")),
        ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor("#1F2A44")),

        # Total row (if exists)
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#E8EAF0")),
    ]))

    elements.append(table)

    # =============================================
    # HEADER & FOOTER FUNCTIONS
    # =============================================

    def header_footer(canvas, doc):
        canvas.saveState()

        # =============================================
        # HEADER SECTION
        # =============================================

        # Header background (subtle gradient effect with rectangle)
        canvas.setFillColor(colors.HexColor("#F8F9FA"))
        canvas.rect(0, A4[1] - 5.2 * cm, A4[0], 5.2 * cm, fill=True, stroke=False)  # Reduced from 6.5cm

        # Header dimensions
        header_y_base = A4[1] - 2 * cm
        left_margin = 2 * cm
        right_margin = A4[0] - 2 * cm

        # =============================================
        # COMPANY NAME (LEFT - LARGER & BOLD)
        # =============================================
        canvas.setFillColor(colors.HexColor("#1F2A44"))
        canvas.setFont("Helvetica-Bold", 22)
        canvas.drawString(left_margin, header_y_base, "Tuniplast")

        # =============================================
        # COMPANY INFORMATION (LEFT - PROFESSIONAL SPACING)
        # =============================================
        info_y = header_y_base - 0.9 * cm
        line_height = 0.45 * cm

        canvas.setFillColor(colors.HexColor("#4A5568"))
        canvas.setFont("Helvetica", 7)

        info_lines = [
            "KM 6 ROUTE DE TUNIS SOLIMAN NABEUL, NABEUL",
            "Représentant commercial : Sami Nasraoui",
            "Email : nasrauisami@gmail.com",
            "Tél : 20 400 041",
            "TVA: 1500874L/A/M/000"
        ]
        
        for i, line in enumerate(info_lines):
            canvas.drawString(left_margin + 0.1 * cm, info_y - (i * line_height), line)

        # Calculate info box positions
        info_box_height = len(info_lines) * line_height
        info_box_top = info_y
        info_box_bottom = info_y - info_box_height

        # =============================================
        # LOGO (RIGHT - LEVEL WITH FIRST INFO LINE)
        # =============================================
        logo_path = resource_path("assets/logo.png")
        logo_size = 2.5 * cm  # Slightly smaller logo
        logo_x = right_margin - logo_size
        logo_y = info_y - (logo_size / 2) + 0.15 * cm  # Align center of logo with first info line

        if logo_path and os.path.exists(logo_path):
            try:
                canvas.drawImage(
                    ImageReader(logo_path),
                    logo_x,
                    logo_y,
                    width=logo_size,
                    height=logo_size,
                    mask="auto",
                    preserveAspectRatio=True
                )
            except Exception as e:
                # Logo placeholder if image fails
                canvas.setFillColor(colors.HexColor("#4A90E2"))
                canvas.rect(logo_x, logo_y, logo_size, logo_size, fill=True, stroke=True)
                canvas.setFillColor(colors.white)
                canvas.setFont("Helvetica-Bold", 10)
                canvas.drawCentredString(
                    logo_x + logo_size/2,
                    logo_y + logo_size/2,
                    "LOGO"
                )

        # =============================================
        # ELEGANT SEPARATOR LINE
        # =============================================
        separator_y = header_y_base - 3 * cm  # Adjusted for smaller header
        canvas.setStrokeColor(colors.HexColor("#1F2A44"))
        canvas.setLineWidth(1.5)
        canvas.line(left_margin, separator_y, right_margin, separator_y)

        # Accent line (thinner, below main line)
        canvas.setStrokeColor(colors.HexColor("#4A90E2"))
        canvas.setLineWidth(0.5)
        canvas.line(left_margin, separator_y - 0.15 * cm, right_margin, separator_y - 0.15 * cm)

        # =============================================
        # FOOTER SECTION
        # =============================================

        footer_y = 2 * cm

        # Footer separator line
        canvas.setStrokeColor(colors.HexColor("#E0E0E0"))
        canvas.setLineWidth(0.5)
        canvas.line(left_margin, footer_y + 0.5 * cm, right_margin, footer_y + 0.5 * cm)

        # Footer text
        canvas.setFillColor(colors.HexColor("#718096"))
        canvas.setFont("Helvetica", 8.5)

        # Page number (left)
        canvas.drawString(left_margin, footer_y, f"Page {doc.page}")

        # Generated date (right)
        date_str = datetime.now().strftime('%d/%m/%Y à %H:%M')
        canvas.drawRightString(right_margin, footer_y, f"Généré le {date_str}")

        canvas.restoreState()

    # =============================================
    # BUILD PDF
    # =============================================
    doc.build(elements, onFirstPage=header_footer, onLaterPages=header_footer)


class EditClientDialog(QDialog):
        def __init__(self, client_data, parent=None):
            super().__init__(parent)
            self.setWindowTitle("Modifier un client")
            #this i
            self.setModal(False) if self.parent() and isinstance(self.parent(), QDialog) else self.setModal(True)
            self.resize(400, 200)

            layout = QVBoxLayout(self)

            # Formulaire
            form_layout = QFormLayout()
            
            self.nom_edit = QLineEdit()
            self.nom_edit.setText(client_data.get('nom', ''))
            self.nom_edit.setPlaceholderText("Nom du client")
            form_layout.addRow("Nom:", self.nom_edit)

            self.tel_edit = QLineEdit()
            self.tel_edit.setText(client_data.get('telephone', ''))
            self.tel_edit.setPlaceholderText("Numéro de téléphone")
            form_layout.addRow("Téléphone:", self.tel_edit)

            self.adresse_edit = QLineEdit()
            self.adresse_edit.setText(client_data.get('adresse', ''))
            self.adresse_edit.setPlaceholderText("Adresse")
            form_layout.addRow("Adresse:", self.adresse_edit)

            self.email_edit = QLineEdit()
            self.email_edit.setText(client_data.get('email', ''))
            self.email_edit.setPlaceholderText("Adresse email")
            form_layout.addRow("Email:", self.email_edit)

            layout.addLayout(form_layout)

            # Boutons
            buttons = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
                Qt.Orientation.Horizontal, self
            )

            # Change button text
            buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Enregistrer")
            buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Fermer")

            buttons.accepted.connect(self.accept)
            buttons.rejected.connect(self.reject)
            layout.addWidget(buttons)

        def get_data(self):
            return {
                'nom': self.nom_edit.text().strip(),
                'telephone': self.tel_edit.text().strip(),
                'adresse': self.adresse_edit.text().strip(),
                'email': self.email_edit.text().strip()
            }


class AddVenteDialog(QDialog):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.setWindowTitle("Nouvelle Vente")
            self.setModal(False) if self.parent() and isinstance(self.parent(), QDialog) else self.setModal(True)
            self.resize(350, 150)

            layout = QVBoxLayout(self)

            # Formulaire
            form_layout = QFormLayout()

            self.ref_edit = QLineEdit()
            self.ref_edit.setText(generate_reference())
            self.ref_edit.setPlaceholderText("Référence de la vente")
            form_layout.addRow("Référence:", self.ref_edit)

            self.desc_edit = QLineEdit()
            self.desc_edit.setPlaceholderText("Description des items vendus")
            form_layout.addRow("Description:", self.desc_edit)

            self.montant_edit = QLineEdit()
            self.montant_edit.setPlaceholderText("0.000")
            form_layout.addRow("Montant total (DT):", self.montant_edit)

            layout.addLayout(form_layout)

            # Boutons
            buttons = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
                Qt.Orientation.Horizontal, self
            )

            # Change button text
            buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Enregistrer")
            buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Fermer")

            buttons.accepted.connect(self.accept)
            buttons.rejected.connect(self.reject)
            layout.addWidget(buttons)

        def get_data(self):
            return {
                'reference': self.ref_edit.text().strip(),
                'description': self.desc_edit.text().strip(),
                'montant': self.montant_edit.text().strip()
            }


class EditVenteDialog(QDialog):
        def __init__(self, vente_data, parent=None):
            super().__init__(parent)
            self.setWindowTitle("Modifier une vente")
            self.setModal(False) if self.parent() and isinstance(self.parent(), QDialog) else self.setModal(True)
            self.resize(400, 190)

            layout = QVBoxLayout(self)

            # Formulaire
            form_layout = QFormLayout()

            self.ref_edit = QLineEdit()
            self.ref_edit.setText(vente_data.get('reference', ''))
            self.ref_edit.setPlaceholderText("Référence de la vente")
            form_layout.addRow("Référence:", self.ref_edit)

            self.desc_edit = QLineEdit()
            self.desc_edit.setText(vente_data.get('description', ''))
            self.desc_edit.setPlaceholderText("Description des items vendus")
            form_layout.addRow("Description:", self.desc_edit)

            self.montant_edit = QLineEdit()
            self.montant_edit.setText(vente_data.get('montant', ''))
            self.montant_edit.setPlaceholderText("0.000")
            form_layout.addRow("Montant total (DT):", self.montant_edit)

            # # Nouveau champ pour modifier le reste
            # self.reste_edit = QLineEdit()
            # self.reste_edit.setText(vente_data.get('reste', ''))
            # self.reste_edit.setPlaceholderText("0.000")
            # form_layout.addRow("Reste (DT):", self.reste_edit)

            layout.addLayout(form_layout)

            # Boutons
            buttons = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
                Qt.Orientation.Horizontal, self
            )

            # Change button text
            buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Enregistrer")
            buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Fermer")

            buttons.accepted.connect(self.accept)
            buttons.rejected.connect(self.reject)
            layout.addWidget(buttons)

        def get_data(self):
            return {
                'reference': self.ref_edit.text().strip(),
                'description': self.desc_edit.text().strip(),
                'montant': self.montant_edit.text().strip(),
                # 'reste': self.reste_edit.text().strip()
            }


class AddClientDialog(QDialog):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.setWindowTitle("Ajouter un client")
            self.setModal(False) if self.parent() and isinstance(self.parent(), QDialog) else self.setModal(True)
            self.resize(400, 200)

            layout = QVBoxLayout(self)

            # Formulaire
            form_layout = QFormLayout()

            self.nom_edit = QLineEdit()
            self.nom_edit.setPlaceholderText("Nom du client")
            form_layout.addRow("Nom:", self.nom_edit)

            self.tel_edit = QLineEdit()
            self.tel_edit.setPlaceholderText("Numéro de téléphone")
            form_layout.addRow("Téléphone:", self.tel_edit)

            self.adresse_edit = QLineEdit()
            self.adresse_edit.setPlaceholderText("Adresse")
            form_layout.addRow("Adresse:", self.adresse_edit)

            self.email_edit = QLineEdit()
            self.email_edit.setPlaceholderText("Adresse email")
            form_layout.addRow("Email:", self.email_edit)

            layout.addLayout(form_layout)

            # Boutons
            buttons = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
                Qt.Orientation.Horizontal, self
            )

            # Change button text
            buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Enregistrer")
            buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Fermer")

            buttons.accepted.connect(self.accept)
            buttons.rejected.connect(self.reject)
            layout.addWidget(buttons)

        def get_data(self):
            return {
                'nom': self.nom_edit.text().strip(),
                'telephone': self.tel_edit.text().strip(),
                'adresse': self.adresse_edit.text().strip(),
                'email': self.email_edit.text().strip()
            }
        
class HistDialog(QDialog):
    def __init__(self, history, vente_id=None, parent=None):
        super().__init__(parent)
        self.vente_id = vente_id
        self._empty_label = None
        self.setWindowTitle("Historique des paiements")
        self.resize(1000, 400)

        layout = QVBoxLayout(self)

        # Table
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels([
            "Date", "Montant (DT)", "Mode", "Actions"
        ])
        
        # Column widths
        self.table.setColumnWidth(0, 120)  # Date
        self.table.setColumnWidth(1, 100)  # Montant
        self.table.setColumnWidth(2, 120)  # Mode
        self.table.setColumnWidth(3, 140)  # Actions

        header = self.table.horizontalHeader()

        # Fixed columns
        header.setSectionResizeMode(0, header.ResizeMode.Stretch)   # Date
        header.setSectionResizeMode(1, header.ResizeMode.Stretch)   # Montant
        header.setSectionResizeMode(2, header.ResizeMode.Stretch)   # Mode
        header.setSectionResizeMode(3, header.ResizeMode.Fixed)     # Actions

        # Stretch last section
        self.table.horizontalHeader().setStretchLastSection(True)

        # Table behavior
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setAlternatingRowColors(True)

        layout.addWidget(self.table)

        # Fill data
        self.load_history()

        # Add print button
        btn_pdf = QPushButton("Imprimer Historique")
        btn_pdf.clicked.connect(self.print_history)
        layout.addWidget(btn_pdf)

    def _set_empty_state(self, show):
        if show:
            if not self._empty_label:
                empty = QLabel("Aucun paiement enregistre.")
                empty.setAlignment(Qt.AlignCenter)
                empty.setStyleSheet("color: #666;")
                self._empty_label = empty
                self.layout().insertWidget(0, empty)
        else:
            if self._empty_label:
                self.layout().removeWidget(self._empty_label)
                self._empty_label.setParent(None)
                self._empty_label = None

    def load_history(self):
        if not self.vente_id:
            self.table.setRowCount(0)
            self._set_empty_state(True)
            return

        conn = get_connection()
        c = conn.cursor()
        c.execute("""
            SELECT p.id, p.date, p.montant, p.mode, p.note
            FROM paiements p
            WHERE p.vente_id=?
            ORDER BY p.date DESC
        """, (self.vente_id,))
        rows = c.fetchall()
        conn.close()

        self.table.setRowCount(0)
        if not rows:
            self._set_empty_state(True)
            return
        self._set_empty_state(False)

        for row_idx, (pid, date_paiement, montant, mode, note) in enumerate(rows):
            self.table.insertRow(row_idx)
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(date_paiement)))
            self.table.setItem(row_idx, 1, QTableWidgetItem(f"{montant:.3f}"))
            self.table.setItem(row_idx, 2, QTableWidgetItem(mode))

            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(1, 1, 1, 1)
            actions_layout.setSpacing(4)

            btn_edit = QPushButton("Modifier")
            btn_edit.setToolTip("Modifier")
            btn_edit.setStyleSheet("""
                QPushButton {
                    background-color: #0078D4;
                    color: white;
                    border: none;
                    padding: 2px 3px;
                    border-radius: 3px;
                    font-size: 7pt;
                    text-align: center;
                    min-width: 40px;
                    max-width: 80px;
                }
                QPushButton:hover {
                    background-color: #106EBE;
                }
            """)
            btn_edit.clicked.connect(lambda _, x=pid, m=montant, md=mode, n=note: self.edit_payment(x, m, md, n))
            actions_layout.addWidget(btn_edit)

            btn_delete = QPushButton("Supprimer")
            btn_delete.setToolTip("Supprimer")
            btn_delete.setStyleSheet("""
                QPushButton {
                    background-color: #D13438;
                    color: white;
                    border: none;
                    padding: 2px 3px;
                    border-radius: 3px;
                    font-size: 7pt;
                    text-align: center;
                    min-width: 40px;
                    max-width: 80px;
                }
                QPushButton:hover {
                    background-color: #B91C1C;
                }
            """)
            btn_delete.clicked.connect(lambda _, x=pid: self.delete_payment(x))
            actions_layout.addWidget(btn_delete)

            self.table.setCellWidget(row_idx, 3, actions_widget)

    def edit_payment(self, payment_id, current_amount, current_mode, current_note):
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("SELECT montant_total FROM ventes WHERE id=?", (self.vente_id,))
            total_sale = c.fetchone()[0] or 0
            c.execute("""
                SELECT IFNULL(SUM(montant), 0)
                FROM paiements
                WHERE vente_id=? AND id<>?
            """, (self.vente_id, payment_id))
            others_sum = c.fetchone()[0] or 0
            conn.close()

            max_amount = max(total_sale - others_sum, 0)
            montant, ok = QInputDialog.getDouble(
                self, "Modifier Paiement",
                f"Montant du paiement (max {max_amount:.3f} DT):",
                current_amount, 0.001, max_amount, 3
            )
            if not ok:
                return

            modes = ["Especes", "Carte Bancaire", "Cheque", "Virement Bancaire"]
            try:
                current_index = modes.index(current_mode)
            except ValueError:
                current_index = 0
            mode, ok_mode = QInputDialog.getItem(
                self, "Mode de Paiement",
                "Selectionnez le mode de paiement:",
                modes, current_index, False
            )
            if not ok_mode:
                return

            # note, ok_note = QInputDialog.getText(
            #     self, "Note", "Note (optionnel):", text=current_note or ""
            # )
            # if not ok_note:
            #     return

            conn = get_connection()
            c = conn.cursor()
            c.execute("""
                UPDATE paiements
                SET montant=?, mode=?
                WHERE id=?
            """, (montant, mode, payment_id))
            conn.commit()
            conn.close()

            self.load_history()
            self._refresh_parent()
            QMessageBox.information(self, "Succes", "Paiement modifie avec succes!")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la modification:{str(e)}")

    def delete_payment(self, payment_id):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Confirmation de suppression")
        msg_box.setText("Etes-vous sur de vouloir supprimer ce paiement ?")
        btn_oui = msg_box.addButton("Oui", QMessageBox.ButtonRole.YesRole)
        btn_non = msg_box.addButton("Non", QMessageBox.ButtonRole.NoRole)
        msg_box.setDefaultButton(btn_non)
        msg_box.exec()

        if msg_box.clickedButton() != btn_oui:
            return

        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("DELETE FROM paiements WHERE id=?", (payment_id,))
            conn.commit()
            conn.close()

            self.load_history()
            self._refresh_parent()
            QMessageBox.information(self, "Succes", "Paiement supprime avec succes!")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la suppression:{str(e)}")

    def _refresh_parent(self):
        parent = self.parent()
        if parent and hasattr(parent, "refresh_ventes"):
            parent.refresh_ventes()
        if parent and hasattr(parent, "update_credit"):
            parent.update_credit()

    def print_history(self):
        from datetime import datetime
        # Get reference, client name, and description
        conn = get_connection()
        c = conn.cursor()
        c.execute("""
            SELECT v.reference, c.nom, v.description, v.montant_total
            FROM ventes v
            JOIN clients c ON v.client_id = c.id
            WHERE v.id=?
        """, (self.vente_id,))
        result = c.fetchone()

        # Calculate total payments made for this sale
        c.execute("""
            SELECT COALESCE(SUM(montant), 0) as total_payments
            FROM paiements
            WHERE vente_id=?
        """, (self.vente_id,))
        payment_result = c.fetchone()
        conn.close()

        if result:
            ref, client_nom, description, montant_total = result
            total_payments = payment_result[0] if payment_result else 0
            reste_a_payer = montant_total - total_payments

            title = f"Historique des Paiements - Vente: {ref}"

            # Create client info for display above title
            client_info = f"Client: {client_nom} | Description: {description} | Montant Total: {montant_total:.3f} DT | Reste a payer: {reste_a_payer:.3f} DT"

            default_filename = f"historique_paiements_{ref.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            filename, _ = QFileDialog.getSaveFileName(self, "Exporter en PDF", default_filename, "PDF Files (*.pdf)")
            if filename:
                export_table_to_pdf(self.table, filename, title, client_info, exclude_columns=[3])
                QMessageBox.information(self, "Succes", f"Le PDF a ete exporte avec succes :{filename}")
        else:
            QMessageBox.warning(self, "Erreur", "Impossible de recuperer les informations de la vente.")

class AddPaiementDialog(QDialog):
    def __init__(self, max_amount, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ajouter un paiement")
        self.resize(300, 150)

        layout = QVBoxLayout(self)

        form_layout = QFormLayout()

        self.montant_edit = QLineEdit()
        self.montant_edit.setPlaceholderText(f"Montant (max {max_amount:.3f} DT)")
        form_layout.addRow("Montant (DT):", self.montant_edit)

        self.mode_edit = QLineEdit()
        self.mode_edit.setPlaceholderText("Mode de paiement (ex: Espèces, Carte)")
        form_layout.addRow("Mode de paiement:", self.mode_edit)

        self.note_edit = QLineEdit()
        self.note_edit.setPlaceholderText("Note (optionnel)")
        form_layout.addRow("Note:", self.note_edit)

        layout.addLayout(form_layout)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            Qt.Orientation.Horizontal, self
        )

        buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Enregistrer")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Fermer")

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_data(self):
        return {
            'montant': self.montant_edit.text().strip(),
            'mode': self.mode_edit.text().strip(),
            'note': self.note_edit.text().strip()
        }


class App(QWidget):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("ClientFlow – Suivi Clients")
            self.resize(1200, 700)
            # Appliquer un style professionnel
            self.setStyleSheet("""
                QWidget {
                    font-family: 'Segoe UI', Arial, sans-serif;
                    font-size: 10pt;
                }
                QPushButton {
                    background-color: #0078D4;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #106EBE;
                }
                QPushButton:pressed {
                    background-color: #005A9E;
                }
                QTableWidget {
                    gridline-color: #CCCCCC;
                    selection-background-color: #E6F3FF;
                    font-size: 9pt;
                }
                QTableWidget::item {
                    padding: 4px;
                    font-size: 9pt;
                }
                QLineEdit, QDateEdit {
                    padding: 5px;
                    border: 1px solid #CCCCCC;
                    border-radius: 3px;
                }
                QLabel {
                    font-weight: bold;
                }
            """)
            self.layout = QVBoxLayout(self)



            

            

                    # Search layout
            search_layout = QHBoxLayout()
            search_layout.addWidget(QLabel("🔍 Rechercher client:"))

            self.search_edit = QLineEdit()
            self.search_edit.setPlaceholderText("Tapez pour rechercher...")
            self.search_edit.textChanged.connect(self.filter_clients)
            search_layout.addWidget(self.search_edit)

            # Stretch pushes the button to the right
            search_layout.addStretch()

            # Add the "À Propos" button on the same row
            btn_about = self.top_button("ℹ À Propos")
            btn_about.clicked.connect(lambda: AboutDialog(self).exec())
            search_layout.addWidget(btn_about)

            # Add the entire row to the main layout
            self.layout.addLayout(search_layout)


            # Buttons layout
            btn_layout = QHBoxLayout()
            self.btn_add = QPushButton("➕ Ajouter client")
            self.btn_add.setToolTip("Ajouter un nouveau client à la base de données")
            self.btn_add.clicked.connect(self.add_client)
            self.btn_pdf_clients = QPushButton("📄 PDF clients")
            self.btn_pdf_clients.setToolTip("Exporter la liste des clients en PDF")
            self.btn_pdf_clients.clicked.connect(self.pdf_clients)


            # #reset database button
            # btn_reset_db = self.top_button("⚠ Réinitialiser la base de données")
            # btn_reset_db.setStyleSheet("""
            #     QPushButton {
            #         background-color: transparent;
            #         border: 1px solid #E53E3E;
            #         color: #E53E3E;
            #         padding: 6px 10px;
            #         font-weight: 500;
            #         border-radius: 6px;
            #     }
            #     QPushButton:hover {
            #         background-color: #FEE2E2;
            #     }
            #     QPushButton:pressed {
            #         background-color: #FEE2E2;
            #     }
            # """)
            # btn_reset_db.clicked.connect(self.reset_database)
            # self.layout.addWidget(btn_reset_db, alignment=Qt.AlignmentFlag.AlignRight)
   
            # btn_layout.addWidget(btn_reset_db)

            btn_layout.addWidget(self.btn_add)
            btn_layout.addWidget(self.btn_pdf_clients)
            
            btn_layout.addStretch()

            self.layout.addLayout(btn_layout)

            self.table = QTableWidget(0, 7)
            self.table.setHorizontalHeaderLabels(
                ["Client", "Téléphone", "Adresse", "Email", "Crédit", "Reste à payer", "Actions"]
            )
            # Configuration de l'espacement des colonnes (plus compact)
            self.table.setColumnWidth(0, 160)  # Client
            self.table.setColumnWidth(1, 100)  # Téléphone
            self.table.setColumnWidth(2, 170)  # Adresse
            self.table.setColumnWidth(3, 170)  # Email
            self.table.setColumnWidth(4, 100)  # Crédit
            self.table.setColumnWidth(5, 110)  # Reste à payer
            self.table.setColumnWidth(6, 150)  # Actions

            header = self.table.horizontalHeader()

            # Fixed columns
            header.setSectionResizeMode(1, header.ResizeMode.Fixed)   # Téléphone
            header.setSectionResizeMode(4, header.ResizeMode.Fixed)   # Crédit
            header.setSectionResizeMode(5, header.ResizeMode.Fixed)   # Reste à payer
            header.setSectionResizeMode(6, header.ResizeMode.Fixed)   # Actions

            # Stretch text columns
            header.setSectionResizeMode(0, header.ResizeMode.Stretch) # Client
            header.setSectionResizeMode(2, header.ResizeMode.Stretch) # Adresse
            header.setSectionResizeMode(3, header.ResizeMode.Stretch) # Email

            
            # Ne pas étirer la dernière colonne pour garder la table compacte
            self.table.horizontalHeader().setStretchLastSection(False)
           

            self.layout.addWidget(self.btn_add)
            self.layout.addWidget(self.table)

            # Totals section
            totals_layout = QHBoxLayout()
            self.total_credit_label = QLabel("Total Crédit: 0.000 DT")
            self.total_paye_label = QLabel("Total Payé: 0.000 DT")
            self.total_reste_label = QLabel("Total Reste: 0.000 DT")
            totals_layout.addStretch()
            totals_layout.addWidget(self.total_credit_label)
            totals_layout.addWidget(self.total_paye_label)
            totals_layout.addWidget(self.total_reste_label)
            self.layout.addLayout(totals_layout)

            self.load_clients()

        def top_button(self, text):
            btn = QPushButton(text)
            btn.setFixedHeight(30)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    padding: 6px 10px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #e6e6e6;
                    border-radius: 6px;
                }
            """)
            return btn

                 # ---------------- DATA ----------------
        
        def load_clients(self):
            conn = get_connection()
            c = conn.cursor()
            c.execute("""
                SELECT c.id, c.nom, c.telephone, c.adresse, c.email,
                    IFNULL(SUM(v.montant_total), 0) AS total_credit,
                    IFNULL(SUM(v.montant_total - IFNULL(v.paye, 0)), 0) AS total_reste
                FROM clients c
                LEFT JOIN (
                    SELECT v.id, v.client_id, v.montant_total,
                        IFNULL(SUM(p.montant), 0) AS paye
                    FROM ventes v
                    LEFT JOIN paiements p ON v.id = p.vente_id
                    GROUP BY v.id, v.client_id, v.montant_total
                ) v ON c.id = v.client_id
                GROUP BY c.id, c.nom, c.telephone, c.adresse, c.email
                ORDER BY c.nom
            """)
            rows = c.fetchall()
            conn.close()

            self.clients_cache = rows
            self.populate_table(rows)
            print(self.clients_cache)

            # Calculate totals
            conn = get_connection()
            c = conn.cursor()
            c.execute("""
                SELECT SUM(montant_total) FROM ventes
            """)
            total_credit = c.fetchone()[0] or 0
            c.execute("""
                SELECT SUM(paye), SUM(montant_total - paye) FROM (
                    SELECT v.id, v.montant_total, IFNULL(SUM(p.montant), 0) as paye
                    FROM ventes v
                    LEFT JOIN paiements p ON v.id = p.vente_id
                    GROUP BY v.id, v.montant_total
                )
            """)
            total_paye, total_reste = c.fetchone()
            total_paye = total_paye or 0
            total_reste = total_reste or 0
            conn.close()
            self.total_credit_label.setText(f"Total Crédit: {total_credit:.3f} DT")
            self.total_paye_label.setText(f"Total Payé: {total_paye:.3f} DT")
            self.total_reste_label.setText(f"Total Reste: {total_reste:.3f} DT")

        def populate_table(self, rows):
            self.table.setUpdatesEnabled(False)
            self.table.setRowCount(0)

            for r, (cid, nom, tel, adr, eml, credit, reste) in enumerate(rows):
                self.table.insertRow(r)
                self.table.setItem(r, 0, QTableWidgetItem(nom))
                self.table.setItem(r, 1, QTableWidgetItem(tel or ""))
                self.table.setItem(r, 2, QTableWidgetItem(adr or ""))
                self.table.setItem(r, 3, QTableWidgetItem(eml or ""))
                self.table.setItem(r, 4, QTableWidgetItem(f"{credit:.3f} DT"))
                self.table.setItem(r, 5, QTableWidgetItem(f"{reste:.3f} DT"))

                action_widget = QWidget()
                action_layout = QHBoxLayout(action_widget)
                action_layout.setContentsMargins(2, 2, 2, 2)

                btn_del = QPushButton("🗑️")
                btn_del.clicked.connect(lambda _, x=cid, n=nom: self.delete_client(x, n))
                action_layout.addWidget(btn_del)



                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(1, 1, 1, 1)
                actions_layout.setSpacing(1)

                # Bouton Détails
                btn_view = QPushButton("👁️ Détails")
                btn_view.setStyleSheet("""
                    QPushButton {
                        background-color: #28A745;
                        color: white;
                        border: none;
                        padding: 2px 3px;
                        border-radius: 3px;
                        font-size: 7pt;
                        text-align: center;
                        min-width: 40px;
                        max-width: 80px;
                    }
                    QPushButton:hover {
                        background-color: #218838;
                    }
                """)
                btn_view.clicked.connect(lambda _, x=cid: self.client_detail(x))
                actions_layout.addWidget(btn_view)

                # Bouton Modifier
                btn_edit = QPushButton("✏️ Modifier")
                btn_edit.setStyleSheet("""
                    QPushButton {
                        background-color: #0078D4;
                        color: white;
                        border: none;
                        padding: 2px 3px;
                        border-radius: 3px;
                        font-size: 7pt;
                        text-align: center;
                        min-width: 40px;
                        max-width: 80px;
                    }
                    QPushButton:hover {
                        background-color: #106EBE;
                    }
                """)
                btn_edit.clicked.connect(lambda _, x=cid: self.edit_client(x))
                actions_layout.addWidget(btn_edit)

                # Bouton de suppression
                btn_delete = QPushButton("🗑️ Suppr")
                btn_delete.setStyleSheet("""
                    QPushButton {
                        background-color: #D13438;
                        color: white;
                        border: none;
                        padding: 2px 3px;
                        border-radius: 3px;
                        font-size: 7pt;
                        text-align: center;
                        min-width: 40px;
                        max-width: 80px;
                    }
                    QPushButton:hover {
                        background-color: #B91C1C;
                    }
                """)
                btn_delete.clicked.connect(lambda _, x=cid, n=nom: self.delete_client(x, n))
                actions_layout.addWidget(btn_delete)

                self.table.setCellWidget(r, 6, actions_widget)


            

            self.table.setUpdatesEnabled(True)

        def filter_clients(self):
            text = self.search_edit.text().lower().strip()
            if not text:
                self.populate_table(self.clients_cache)
                return

            filtered = [
                r for r in self.clients_cache
                if text in (r[1] or "").lower()
                or text in (r[2] or "").lower()
                or text in (r[3] or "").lower()
                or text in (r[4] or "").lower()
            ]
            self.populate_table(filtered)
            print(filtered)

        def delete_client(self, client_id, client_name):
            """Supprime un client après confirmation"""
            
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Confirmation de suppression")
            msg_box.setText(
                f"Êtes-vous sûr de vouloir supprimer le client '{client_name}' ?\n\n"
                "Cette action supprimera également toutes ses ventes et paiements associés."
            )
            
            # Boutons personnalisés en français
            btn_oui = msg_box.addButton("Oui", QMessageBox.ButtonRole.YesRole)
            btn_non = msg_box.addButton("Non", QMessageBox.ButtonRole.NoRole)
            
            msg_box.setDefaultButton(btn_non)
            msg_box.exec()
            
            if msg_box.clickedButton() == btn_oui:
                try:
                    conn = get_connection()
                    c = conn.cursor()
                    
                    # Supprimer les paiements associés aux ventes du client
                    c.execute("DELETE FROM paiements WHERE vente_id IN (SELECT id FROM ventes WHERE client_id=?)", (client_id,))
                    
                    # Supprimer les ventes du client
                    c.execute("DELETE FROM ventes WHERE client_id=?", (client_id,))
                    
                    # Supprimer le client
                    c.execute("DELETE FROM clients WHERE id=?", (client_id,))
                    
                    conn.commit()
                    conn.close()
                    
                    QMessageBox.information(self, "Succès", f"Client '{client_name}' supprimé avec succès.")
                    
                    self.load_clients()  # Recharger la liste
                    
                except Exception as e:
                    QMessageBox.critical(self, "Erreur", f"Erreur lors de la suppression:\n{str(e)}")


        def edit_client(self, client_id):
            """Modifie un client existant"""
            try:
                # Récupérer les données actuelles du client
                conn = get_connection()
                c = conn.cursor()
                c.execute("SELECT nom, telephone, adresse, email FROM clients WHERE id=?", (client_id,))
                client_data = c.fetchone()
                conn.close()

                if not client_data:
                    QMessageBox.warning(self, "Erreur", "Client introuvable.")
                    return

                # Convertir en dictionnaire
                client_dict = {
                    'nom': client_data[0] or '',
                    'telephone': client_data[1] or '',
                    'adresse': client_data[2] or '',
                    'email': client_data[3] or ''
                }

                # Ouvrir la boîte de dialogue d'édition
                dialog = EditClientDialog(client_dict, self)
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    data = dialog.get_data()
                    if not data['nom'].strip():
                        QMessageBox.warning(self, "Erreur", "Le nom du client est obligatoire.")
                        return

                    # Mettre à jour le client
                    conn = get_connection()
                    c = conn.cursor()
                    c.execute("""
                        UPDATE clients 
                        SET nom=?, telephone=?, adresse=?, email=?
                        WHERE id=?
                    """, (data['nom'].strip(), data['telephone'].strip(), 
                        data['adresse'].strip(), data['email'].strip(), client_id))
                    conn.commit()
                    conn.close()

                    self.load_clients()
                    QMessageBox.information(self, "Succès", "Client modifié avec succès!")

            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors de la modification:\n{str(e)}")

            
        def pdf_clients(self):
            # Générer un nom de fichier par défaut avec la date
            from datetime import datetime
            default_filename = f"liste_clients_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            filename, _ = QFileDialog.getSaveFileName(self, "Exporter en PDF", default_filename, "PDF Files (*.pdf)")
            if filename:
                # Exclure la colonne "Actions" (6) qui contient les boutons
                export_table_to_pdf(self.table, filename, "Liste des Clients", exclude_columns=[6])
                QMessageBox.information(self, "Succès", f"Le PDF a été exporté avec succès :\n{filename}")

        def reset_database(self):
            # Show confirmation dialog
            reply = QMessageBox.question(
                self, "Confirmer la réinitialisation",
                "⚠️ ATTENTION: Cette action va supprimer TOUTES les données (clients, ventes, paiements).\n\n"
                "Cette action est IRRÉVERSIBLE.\n\n"
                "Voulez-vous vraiment continuer ?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                try:
                    reset_db()
                    # Refresh the table to show empty data
                    self.load_clients()
                    QMessageBox.information(self, "Succès", "La base de données a été réinitialisée avec succès.")
                except Exception as e:
                    QMessageBox.critical(self, "Erreur", f"Erreur lors de la réinitialisation: {str(e)}")

        def seed_database(self):
            # Show confirmation dialog
            reply = QMessageBox.question(
                self, "Confirmer l'ajout de données d'exemple",
                "Cette action va ajouter des données d'exemple à la base de données:\n\n"
                "• 20 clients tunisiens\n"
                "• 50 ventes avec références automatiques\n"
                "• Paiements avec différentes dates et modes\n\n"
                "Les données existantes seront conservées.\n\n"
                "Voulez-vous continuer ?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )

            if reply == QMessageBox.StandardButton.Yes:
                try:
                    from seed_data import seed_all
                    seed_all()
                    # Refresh the table to show new data
                    self.load_clients()
                    QMessageBox.information(self, "Succès", "Les données d'exemple ont été ajoutées avec succès!")
                except Exception as e:
                    QMessageBox.critical(self, "Erreur", f"Erreur lors de l'ajout des données: {str(e)}")

        def add_client(self):
            dialog = AddClientDialog(self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                data = dialog.get_data()
                if not data['nom'].strip():
                    QMessageBox.warning(self, "Erreur", "Le nom du client est obligatoire.")
                    return

                try:
                    conn = get_connection()
                    c = conn.cursor()
                    c.execute("INSERT INTO clients(nom, telephone, adresse, email) VALUES (?,?,?,?)",
                            (data['nom'].strip(), data['telephone'].strip(), data['adresse'].strip(), data['email'].strip()))
                    conn.commit()
                    conn.close()

                    self.load_clients()
                    QMessageBox.information(self, "Succès", "Client ajouté avec succès!")

                except Exception as e:
                    QMessageBox.critical(self, "Erreur", f"Erreur lors de l'ajout du client:\n{str(e)}")

        def client_detail(self, client_id):
            dlg = ClientDetail(client_id)
            dlg.exec()
            self.load_clients()


class ClientDetail(QDialog):
        def __init__(self, client_id):
            super().__init__()
            self.ventes_cache = []  # <-- cache all ventes here
            self.client_id = client_id
            self.use_date_filter = False  # Don't filter by date initially

            #fetch client info
            try:
                conn = get_connection()
                c = conn.cursor()
                c.execute("""
                    SELECT c.nom,
                        IFNULL(SUM(v.montant_total),0) as total_ventes
                    FROM clients c
                    LEFT JOIN ventes v ON c.id=v.client_id
                    WHERE c.id=?
                """, (client_id,))
                client = c.fetchone()
                conn.close()
                if client:
                    client_name = client[0]
                    self.client_total_ventes = client[1] or 0
                else:
                    client_name = "Client Inconnu"
                    self.client_total_ventes = 0
            except Exception as e:
                client_name = "Client Inconnu"
                self.client_total_ventes = 0
                print(f"Erreur lors de la récupération des informations du client: {str(e)}")

            
            #------ui setup------#
            self.setWindowTitle("Fiche Client : " + client_name)
            self.resize(1100, 500)            

            # Style pour la fenêtre détail
            self.setStyleSheet("""
                QWidget {
                    font-family: 'Segoe UI', Arial, sans-serif;
                    font-size: 10pt;
                }
                QPushButton {
                    background-color: #0078D4;
                    color: white;
                    border: none;
                    padding: 6px 12px;
                    border-radius: 3px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #106EBE;
                }
                QTableWidget {
                    gridline-color: #CCCCCC;
                    selection-background-color: #E6F3FF;
                }
                QTableWidget::item {
                    padding: 5px;
                }
                QDateEdit {
                    padding: 3px;
                    border: 1px solid #CCCCCC;
                    border-radius: 3px;
                }
            """)

            self.layout = QVBoxLayout(self)

            # Search layout
            search_layout = QHBoxLayout()
            search_layout.addWidget(QLabel("🔍 Rechercher vente:"))
            self.search_vente_edit = QLineEdit()
            self.search_vente_edit.setPlaceholderText("Référence ou description...")
            self.search_vente_edit.textChanged.connect(self.load_ventes)
            search_layout.addWidget(self.search_vente_edit)

            search_layout.addWidget(QLabel("De:"))
            self.date_from = QDateEdit()
            self.date_from.setDate(QDate.currentDate().addDays(-7))  # Default: last 7 days
            self.date_from.setCalendarPopup(True)  # Activer le calendrier popup
            search_layout.addWidget(self.date_from)

            search_layout.addWidget(QLabel("À:"))
            self.date_to = QDateEdit()
            self.date_to.setDate(QDate.currentDate())
            self.date_to.setCalendarPopup(True)  # Activer le calendrier popup
            search_layout.addWidget(self.date_to)

            self.btn_filter = QPushButton("🔍 Filtrer")
            self.btn_filter.setToolTip("Appliquer le filtre de date")
            self.btn_filter.clicked.connect(self.enable_date_filter)
            search_layout.addWidget(self.btn_filter)

            self.btn_refresh = QPushButton("🔄 Actualiser")
            self.btn_refresh.setToolTip("Réinitialiser les filtres et afficher toutes les ventes")
            self.btn_refresh.clicked.connect(self.refresh_ventes)
            search_layout.addWidget(self.btn_refresh)


            self.btn_pdf = QPushButton("📄 PDF")
            self.btn_pdf.setToolTip("Exporter les ventes du client en PDF")
            self.btn_pdf.clicked.connect(self.pdf_table)
            search_layout.addWidget(self.btn_pdf)

            self.layout.addLayout(search_layout)

            self.btn_vente = QPushButton("➕ Nouvelle vente")
            self.btn_vente.setToolTip("Ajouter une nouvelle vente pour ce client")
            self.btn_vente.clicked.connect(self.add_vente)

            self.table = QTableWidget(0, 7)
            self.table.setHorizontalHeaderLabels(
                ["Date", "Référence", "Description", "Total DT", "Payé DT", "Reste DT", "Actions"]
            )
            # Configuration de l'espacement des colonnes
            self.table.setColumnWidth(0, 100)  # Date
            self.table.setColumnWidth(1, 120)  # Référence
            self.table.setColumnWidth(2, 100)  # Description
            self.table.setColumnWidth(3, 100)  # Total
            self.table.setColumnWidth(4, 100)  # Payé
            self.table.setColumnWidth(5, 100)  # Reste
            self.table.setColumnWidth(6, 200)  # Actions


            header = self.table.horizontalHeader()

            # Fixed columns (numbers & date)
            header.setSectionResizeMode(0, header.ResizeMode.Fixed)  # Date
            header.setSectionResizeMode(1, header.ResizeMode.Fixed)  # Référence
            header.setSectionResizeMode(3, header.ResizeMode.Fixed)  # Total
            header.setSectionResizeMode(4, header.ResizeMode.Fixed)  # Payé
            header.setSectionResizeMode(5, header.ResizeMode.Fixed)  # Reste
            header.setSectionResizeMode(6, header.ResizeMode.Fixed)  # Actions

            # Stretch ONLY description
            header.setSectionResizeMode(2, header.ResizeMode.Stretch)

            
            # Ajuster automatiquement la largeur des colonnes à la fenêtre
            self.table.horizontalHeader().setStretchLastSection(True)
           

            self.layout.addWidget(self.btn_vente)
            self.layout.addWidget(self.table)

            # Client totals section
            
            totals_layout = QHBoxLayout()
            self.client_credit_label = QLabel(f"Crédit Client: {self.client_total_ventes:.3f} DT")
            self.total_paye_client_label = QLabel("Total Payé: 0.000 DT")
            self.total_reste_client_label = QLabel("Total Reste: 0.000 DT")
            #make it bold 
            self.client_credit_label.setStyleSheet("font-weight: bold;")
            self.total_paye_client_label.setStyleSheet("font-weight: bold;")
            self.total_reste_client_label.setStyleSheet("font-weight: bold;")

            totals_layout.addStretch()
            totals_layout.addWidget(self.client_credit_label)
            totals_layout.addWidget(self.total_paye_client_label)
            totals_layout.addWidget(self.total_reste_client_label)

            self.layout.addLayout(totals_layout)

            self.load_ventes()  # load once
            self.apply_filters()      # show filtered view

            self.search_vente_edit.textChanged.connect(self.apply_filters)
            self.btn_filter.clicked.connect(self.enable_date_filter)
            self.btn_refresh.clicked.connect(self.refresh_ventes)

        def load_ventes(self):
            """Load all ventes once and cache them"""
            try:
                conn = get_connection()
                c = conn.cursor()
                c.execute("""
                    SELECT v.id, v.date, v.reference, v.description, v.montant_total,
                        IFNULL(SUM(p.montant), 0) as paye
                    FROM ventes v
                    LEFT JOIN paiements p ON v.id = p.vente_id
                    WHERE v.client_id=?
                    GROUP BY v.id, v.date, v.reference, v.description, v.montant_total
                    ORDER BY v.date DESC
                """, (self.client_id,))
                self.ventes_cache = c.fetchall()
                conn.close()

                # Calculate totals for this client
                total_paye = sum(row[5] for row in self.ventes_cache)
                total_reste = sum(row[4] - row[5] for row in self.ventes_cache)
                self.total_paye_client_label.setText(f"Total Payé: {total_paye:.3f} DT")
                self.total_reste_client_label.setText(f"Total Reste: {total_reste:.3f} DT")

            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement des ventes:\n{str(e)}")
            print(self.ventes_cache)

        def apply_filters(self):
            """Filter ventes from cache instead of querying DB each time"""
            search_text = self.search_vente_edit.text().lower().strip()
            from_date = self.date_from.date().toPython()
            to_date = self.date_to.date().toPython()

            filtered = []

            for vid, d, ref, desc, total, paye in self.ventes_cache:
                date_obj = QDate.fromString(d, "yyyy-MM-dd").toPython() if isinstance(d, str) else d

                # Date filter
                if self.use_date_filter:
                    if date_obj < from_date or date_obj > to_date:
                        continue

                # Search filter
                if search_text:
                    if search_text not in (ref or "").lower() and search_text not in (desc or "").lower():
                        continue

                filtered.append((vid, d, ref, desc, total, paye))

            self.populate_table(filtered)
            print(filtered)

        def update_credit(self):
            try:
                conn = get_connection()
                c = conn.cursor()
                c.execute("""
                    SELECT IFNULL(SUM(v.montant_total),0) as total_ventes
                    FROM clients c
                    LEFT JOIN ventes v ON c.id=v.client_id
                    WHERE c.id=?
                """, (self.client_id,))
                total_ventes = c.fetchone()[0] or 0
                conn.close()
                self.client_total_ventes = total_ventes
                self.client_credit_label.setText(f"Crédit Client: {self.client_total_ventes:.3f} DT")
            except Exception as e:
                print(f"Erreur lors de la mise à jour du crédit: {str(e)}")

        def populate_table(self, rows):
            """Populate table with given rows (from cache)"""
            self.table.setUpdatesEnabled(False)
            self.table.setRowCount(0)

            for row_idx, (vid, d, ref, desc, total, paye) in enumerate(rows):
                reste = total - paye

                self.table.insertRow(row_idx)
                self.table.setItem(row_idx, 0, QTableWidgetItem(d))
                self.table.setItem(row_idx, 1, QTableWidgetItem(ref or ""))
                self.table.setItem(row_idx, 2, QTableWidgetItem(desc or ""))
                self.table.setItem(row_idx, 3, QTableWidgetItem(f"{total:.3f} DT"))
                self.table.setItem(row_idx, 4, QTableWidgetItem(f"{paye:.3f} DT"))
                self.table.setItem(row_idx, 5, QTableWidgetItem(f"{reste:.3f} DT"))

                # Conteneur pour tous les boutons d'action (horizontal)
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(1, 1, 1, 1)
                actions_layout.setSpacing(1)

                #Boutton historique paiements
                btn_hist=QPushButton("📜 Historique")
                btn_hist.setStyleSheet("""
                    QPushButton {
                        background-color: #6C757D;
                        color: white;
                        border: none;
                        padding: 2px 3px;
                        border-radius: 3px;
                        font-size: 7pt;
                        text-align: center;
                        min-width: 40px;
                        max-width: 80px;
                    }
                    QPushButton:hover {
                        background-color: #5A6268;
                    }
                """)
                
                btn_hist.clicked.connect(lambda _, x=vid: self.show_hist(x))
                actions_layout.addWidget(btn_hist)

                # Bouton Payer ou Status
                if reste > 0:
                    btn_action = QPushButton("💰 Payer")
                    btn_action.setStyleSheet("""
                        QPushButton {
                            background-color: #FF8C00;
                            color: white;
                            border: none;
                            padding: 2px 3px;
                            border-radius: 3px;
                            font-size: 7pt;
                            text-align: center;
                            min-width: 40px;
                            max-width: 80px;
                        }
                        QPushButton:hover {
                            background-color: #E67E00;
                        }
                    """)
                    btn_action.clicked.connect(lambda _, x=vid: self.add_paiement(x))
                else:
                    btn_action = QPushButton("✅ Payé")
                    btn_action.setStyleSheet("""
                        QPushButton {
                            background-color: #28A745;
                            color: white;
                            border: none;
                            padding: 2px 3px;
                            border-radius: 3px;
                            font-size: 7pt;
                            text-align: center;
                            min-width: 40px;
                            max-width: 80px;
                        }
                    """)
                    btn_action.setEnabled(False)
                actions_layout.addWidget(btn_action)


                 # Bouton Modifier
                btn_edit = QPushButton("✏️ Modifier")
                btn_edit.setStyleSheet("""
                    QPushButton {
                        background-color: #0078D4;
                        color: white;
                        border: none;
                        padding: 2px 3px;
                                       
                        border-radius: 3px;
                        font-size: 7pt;
                        text-align: center;
                        min-width: 40px;
                        max-width: 80px;
                        
                            
                    }
                    QPushButton:hover {
                        background-color: #106EBE;
                    }
                """)
                btn_edit.clicked.connect(lambda _, x=vid: self.edit_vente(x))
                actions_layout.addWidget(btn_edit)


                # Bouton Supprimer
                btn_delete = QPushButton("🗑️ Suppr")
                btn_delete.setStyleSheet("""
                    QPushButton {
                        background-color: #D13438;
                        color: white;
                        border: none;
                        padding: 2px 3px;
                        border-radius: 3px;
                        font-size: 7pt;
                        text-align: center;
                        min-width: 40px;
                        max-width: 80px;
                    }
                    QPushButton:hover {
                        background-color: #B91C1C;
                    }
                """)
                btn_delete.clicked.connect(lambda _, x=vid, r=ref or f"Vente #{vid}": self.delete_vente(x, r))
                actions_layout.addWidget(btn_delete)

                self.table.setCellWidget(row_idx, 6, actions_widget)

            self.table.setUpdatesEnabled(True)
            
        def enable_date_filter(self):
            self.use_date_filter = True
            self.apply_filters()

        def refresh_ventes(self):
            self.load_ventes()
            self.apply_filters()
            self.update_credit()
            self.use_date_filter = False
            self.search_vente_edit.clear()
            self.date_from.setDate(QDate.currentDate().addDays(-7))
            self.date_to.setDate(QDate.currentDate())
            
        def delete_vente(self, vente_id, vente_ref):
            """Supprime une vente après confirmation"""
            
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Confirmation de suppression")
            msg_box.setText(
                f"Êtes-vous sûr de vouloir supprimer la vente '{vente_ref}' ?\n\n"
                "Cette action supprimera également tous les paiements associés à cette vente."
            )
            
            # Boutons personnalisés en français
            btn_oui = msg_box.addButton("Oui", QMessageBox.ButtonRole.YesRole)
            btn_non = msg_box.addButton("Non", QMessageBox.ButtonRole.NoRole)
            
            msg_box.setDefaultButton(btn_non)  # par défaut Non pour éviter suppression accidentelle
            msg_box.exec()
            
            if msg_box.clickedButton() == btn_oui:
                try:
                    conn = get_connection()
                    c = conn.cursor()
                    
                    # Supprimer les paiements associés à la vente
                    c.execute("DELETE FROM paiements WHERE vente_id=?", (vente_id,))
                    
                    # Supprimer la vente
                    c.execute("DELETE FROM ventes WHERE id=?", (vente_id,))
                    
                    conn.commit()
                    conn.close()
                    
                    QMessageBox.information(self, "Succès", f"Vente '{vente_ref}' supprimée avec succès.")
                    self.refresh_ventes()  # Recharger la liste
                    self.update_credit()
                    
                except Exception as e:
                    QMessageBox.critical(self, "Erreur", f"Erreur lors de la suppression:\n{str(e)}")

        def edit_vente(self, vente_id):
            """Modifie une vente existante"""
            try:
                # Récupérer les données actuelles de la vente
                conn = get_connection()
                c = conn.cursor()
                c.execute("""
                    SELECT v.reference, v.description, v.montant_total, IFNULL(SUM(p.montant), 0) as paye
                    FROM ventes v
                    LEFT JOIN paiements p ON v.id = p.vente_id
                    WHERE v.id=?
                    GROUP BY v.id
                """, (vente_id,))
                vente_data = c.fetchone()
                conn.close()

                if not vente_data:
                    QMessageBox.warning(self, "Erreur", "Vente introuvable.")
                    return

                reference, description, total, paye = vente_data
                current_reste = total - paye

                # Convertir en dictionnaire
                vente_dict = {
                    'reference': reference or '',
                    'description': description or '',
                    'montant': str(total) if total else '',
                    'reste': str(current_reste)
                }

                # Ouvrir la boîte de dialogue d'édition
                dialog = EditVenteDialog(vente_dict, self)
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    data = dialog.get_data()
                    if not data['reference']:
                        QMessageBox.warning(self, "Erreur", "La référence de la vente est obligatoire.")
                        return

                    try:
                        montant = float(data['montant'])
                        if montant <= 0:
                            QMessageBox.warning(self, "Erreur", "Le montant doit être positif.")
                            return
                    except ValueError:
                        QMessageBox.warning(self, "Erreur", "Le montant doit être un nombre valide.")
                        return

                    # try:
                    #     #two decimal points
                    #     new_reste = round(float(data['reste']), 2)
                    #     #new_reste = float(data['reste'])
                    #     if new_reste < 0:
                    #         QMessageBox.warning(self, "Erreur", "Le reste ne peut pas être négatif.")
                    #         return
                    #     if new_reste > montant:
                    #         QMessageBox.warning(self, "Erreur", "Le reste ne peut pas être supérieur au montant total.")
                    #         return
                    # except ValueError:
                    #     QMessageBox.warning(self, "Erreur", "Le reste doit être un nombre valide.")
                    #     return

                    # new_paye = montant - new_reste

                    # Mettre à jour la vente
                    conn = get_connection()
                    c = conn.cursor()
                    c.execute("""
                        UPDATE ventes 
                        SET reference=?, description=?, montant_total=?
                        WHERE id=?
                    """, (data['reference'], data['description'], montant, vente_id))

                    # # Supprimer tous les paiements existants et ajouter un nouveau paiement avec le montant payé calculé
                    # c.execute("DELETE FROM paiements WHERE vente_id=?", (vente_id,))
                    # if new_paye > 0:
                    #     from datetime import date
                    #     c.execute("INSERT INTO paiements (vente_id, montant, date) VALUES (?, ?, ?)", (vente_id, new_paye, date.today().isoformat()))
                    
                    conn.commit()
                    conn.close()

                    self.refresh_ventes()
                    QMessageBox.information(self, "Succès", "Vente modifiée avec succès!")

            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors de la modification:\n{str(e)}")

        def pdf_table(self):
            # Obtenir le nom du client pour le titre
            conn = get_connection()
            c = conn.cursor()
            c.execute("SELECT nom FROM clients WHERE id=?", (self.client_id,))
            client_nom = c.fetchone()[0]
            conn.close()

            title = f"Ventes - Client: {client_nom}"
            # Générer un nom de fichier avec le nom du client
            from datetime import datetime
            default_filename = f"ventes_{client_nom.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            filename, _ = QFileDialog.getSaveFileName(self, "Exporter en PDF", default_filename, "PDF Files (*.pdf)")
            if filename:
                # Exclure la colonne "Actions" (6) qui contient les boutons
                export_table_to_pdf(self.table, filename, title, exclude_columns=[6])
                QMessageBox.information(self, "Succès", f"Le PDF a été exporté avec succès :\n{filename}")

        def add_vente(self):
            dialog = AddVenteDialog(self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                data = dialog.get_data()
                if not data['reference']:
                    QMessageBox.warning(self, "Erreur", "La référence de la vente est obligatoire.")
                    return

                try:
                    montant = float(data['montant'])
                    if montant <= 0:
                        QMessageBox.warning(self, "Erreur", "Le montant doit être positif.")
                        return
                except ValueError:
                    QMessageBox.warning(self, "Erreur", "Le montant doit être un nombre valide.")
                    return

                try:
                    conn = get_connection()
                    c = conn.cursor()
                    c.execute("""
                    INSERT INTO ventes(client_id, date, reference, description, montant_total)
                    VALUES (?,?,?,?,?)
                    """, (self.client_id, date.today().isoformat(), data['reference'], data['description'], montant))
                    conn.commit()
                    conn.close()

                    self.refresh_ventes()
                    QMessageBox.information(self, "Succès", "Vente ajoutée avec succès!")
                    self.update_credit()

                except Exception as e:
                    QMessageBox.critical(self, "Erreur", f"Erreur lors de l'ajout de la vente:\n{str(e)}")

        def add_paiement(self, vente_id):
            # Récupérer le montant restant
            conn = get_connection()
            c = conn.cursor()
            c.execute("""
                SELECT v.montant_total - IFNULL(SUM(p.montant), 0)
                FROM ventes v
                LEFT JOIN paiements p ON v.id = p.vente_id
                WHERE v.id = ?
                GROUP BY v.id, v.montant_total
            """, (vente_id,))
            reste = c.fetchone()[0]
            conn.close()

            if reste <= 0:
                QMessageBox.information(self, "Info", "Cette vente est déjà entièrement payée.")
                return

            montant, ok = QInputDialog.getDouble(self, "Nouveau Paiement",
                                            f"Montant du paiement (DT) - Reste: {reste:.3f} DT:",
                                            0, 0.001, reste, 3)
            
            #add combo box for payment mode in future
            modes = ["Espèces", "Carte Bancaire", "Chèque", "Virement Bancaire"]
            mode, ok_mode = QInputDialog.getItem(self, "Mode de Paiement",
                                              "Sélectionnez le mode de paiement:",
                                            modes, 0, False)
            if not ok_mode:
                return
            #mode = "Espèces"

            # Déterminer la note
            note = "Paiement partiel"
            if montant == reste:
                note = "Paiement complet"

            # ----------------------------
            # Valider le montant
            # ---------------------------- 
            if not ok or montant <= 0:
                return

            try:
                conn = get_connection()
                c = conn.cursor()
                c.execute("""
                INSERT INTO paiements(vente_id, date, montant, mode, note)
                VALUES (?,?,?,?,?)
                """, (vente_id, date.today().isoformat(), montant, mode, note))
                conn.commit()
                conn.close()

                self.refresh_ventes()
                QMessageBox.information(self, "Succès", "Paiement enregistré avec succès!")
                self.update_credit()

            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors de l'enregistrement du paiement:\n{str(e)}")

        def show_hist(self, vente_id):
            # Récupérer l'historique des paiements pour la vente donnée
            try:
                conn = get_connection()
                c = conn.cursor()
                c.execute("""
                    SELECT p.date, p.montant, p.mode, p.note, 
                           c.nom as client_nom, v.description, v.montant_total
                    FROM paiements p
                    JOIN ventes v ON p.vente_id = v.id
                    JOIN clients c ON v.client_id = c.id
                    WHERE p.vente_id=?
                    ORDER BY p.date DESC
                """, (vente_id,))
                hist = c.fetchall()
                conn.close()
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement de l'historique des paiements:\n{str(e)}")
                return
            histDialog = HistDialog(hist, vente_id, self)
            histDialog.exec()
        


def resource_path(relative):
    try:
        base = sys._MEIPASS
    except Exception:
        base = os.path.abspath(".")
    return os.path.join(base, relative)


def get_reportlab_logo_path():
    """
    Return a logo path that ReportLab can render in packaged builds.
    ReportLab can draw JPEGs without Pillow, but PNG often requires Pillow.
    We convert the PNG to a cached JPEG via Qt to avoid missing-image issues.
    """
    logo_png = resource_path("assets/logo.png")
    if not os.path.exists(logo_png):
        return None

    try:
        temp_dir = tempfile.gettempdir()
        logo_jpg = os.path.join(temp_dir, "clientflow_logo.jpg")

        if (not os.path.exists(logo_jpg)) or (os.path.getmtime(logo_jpg) < os.path.getmtime(logo_png)):
            img = QImage(logo_png)
            if img.isNull():
                return logo_png
            img.save(logo_jpg, "JPG")

        return logo_jpg
    except Exception:
        return logo_png


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About ClientFlow")
        self.setFixedSize(200, 200)

        layout = QVBoxLayout(self)

        text = QLabel(
            "<b>ClientFlow</b><br>"
            "Version 1.0.1<br><br>"
            "Client Management System<br><br>"
            "© 2026 Yosri Saadi"
        )
        text.setAlignment(Qt.AlignCenter)

        layout.addWidget(text)


if __name__ == "__main__":
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
        "clientflow.app.1.0"
    )

    init_db()

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(resource_path("assets/icon.ico")))

    splash = QSplashScreen(
        QPixmap(resource_path("assets/icon.ico")),
        Qt.WindowStaysOnTopHint
    )
    splash.show()
    app.processEvents()

    time.sleep(1)  # splash duration

    win = App()
    win.show()
    splash.finish(win)

    sys.exit(app.exec())
