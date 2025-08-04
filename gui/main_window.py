# gui/main_window.py

import sys
import os
import subprocess
import platform

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QLabel, QTableWidget, QTableWidgetItem, QPushButton,
    QHBoxLayout, QLineEdit, QComboBox, QTextEdit, QDateEdit,
    QMessageBox, QHeaderView, QScrollArea
)
from PySide6.QtCore import Qt, QDate
from data.database import SessionLocal
from data.models import JobApplication
from collections import Counter
from PySide6.QtWidgets import QFormLayout

from PySide6.QtWidgets import QFileDialog


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Job Application Tracker")
        self.resize(1000, 700)

        self.session = SessionLocal()

        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout()

        self.title_label = QLabel("Job Application Tracker")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 22px; margin-bottom: 15px;")

        # Buttons for navigation
        self.button_layout = QHBoxLayout()
        self.btn_add_job = QPushButton("➕ Add Job")
        self.btn_view_jobs = QPushButton("📄 View Jobs")
        self.btn_dashboard = QPushButton("📊 Dashboard")

        self.btn_add_job.clicked.connect(self.show_add_job_form)
        self.btn_view_jobs.clicked.connect(self.show_job_list)
        self.btn_dashboard.clicked.connect(self.show_dashboard)
        self.btn_export_csv = QPushButton("📤 Export CSV")
        self.btn_export_csv.clicked.connect(self.export_to_csv)
        self.button_layout.addWidget(self.btn_dashboard)
        self.button_layout.addWidget(self.btn_export_csv)

        self.button_layout.addWidget(self.btn_add_job)
        self.button_layout.addWidget(self.btn_view_jobs)
        self.button_layout.addWidget(self.btn_dashboard)

        # Search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by Company or Position...")
        self.search_input.textChanged.connect(self.show_job_list)

        self.main_layout.addWidget(self.title_label)
        self.main_layout.addLayout(self.button_layout)
        self.main_layout.addWidget(self.search_input)

        # Area to switch views
        self.content_area_widget = QWidget()
        self.content_area_layout = QVBoxLayout()
        self.content_area_widget.setLayout(self.content_area_layout)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.content_area_widget)

        self.main_layout.addWidget(self.scroll)

        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)

        # Initially display job list
        self.show_job_list()

    def clear_content_area(self):
        while self.content_area_layout.count():
            item = self.content_area_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def show_add_job_form(self, job=None):
        self.clear_content_area()

        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        form_layout.setSpacing(10)

        self.company_input = QLineEdit()
        self.position_input = QLineEdit()
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.status_input = QComboBox()
        self.status_input.addItems(["Applied", "Interview Scheduled", "Rejected", "Accepted"])
        self.notes_input = QTextEdit()
        self.description_input = QTextEdit()
        self.cover_letter_path = QLineEdit()
        self.cover_letter_path.setReadOnly(True)
        self.cover_letter_button = QPushButton("📎 Attach Cover Letter")
        self.cover_letter_button.clicked.connect(self.select_cover_letter)

        self.cv_path = QLineEdit()
        self.cv_path.setReadOnly(True)
        self.cv_button = QPushButton("📎 Attach CV / Resume")
        self.cv_button.clicked.connect(self.select_cv)

        if job:
            # Editing an existing job
            self.company_input.setText(job.company)
            self.position_input.setText(job.position)
            self.date_input.setDate(QDate(job.date_applied.year, job.date_applied.month, job.date_applied.day))
            self.status_input.setCurrentText(job.status)
            self.notes_input.setText(job.notes)
            self.description_input.setText(job.description or "")
            self.cover_letter_path.setText(job.cover_letter_path or "")
            self.cv_path.setText(job.cv_path or "")
        else:
            # New job: clear all fields
            self.company_input.clear()
            self.position_input.clear()
            self.date_input.setDate(QDate.currentDate())
            self.status_input.setCurrentIndex(0)
            self.notes_input.clear()
            self.description_input.clear()
            self.cover_letter_path.clear()
            self.cv_path.clear()


        # Attach fields to the form layout
        form_layout.addRow("Company Name:", self.company_input)
        form_layout.addRow("Position:", self.position_input)
        form_layout.addRow("Date Applied:", self.date_input)
        form_layout.addRow("Status:", self.status_input)
        form_layout.addRow("Notes:", self.notes_input)
        form_layout.addRow("Job Description:", self.description_input)

        # Attach Cover Letter with horizontal layout
        cl_layout = QHBoxLayout()
        cl_layout.addWidget(self.cover_letter_path)
        cl_layout.addWidget(self.cover_letter_button)
        form_layout.addRow("Cover Letter:", cl_layout)

        # Attach CV with horizontal layout
        cv_layout = QHBoxLayout()
        cv_layout.addWidget(self.cv_path)
        cv_layout.addWidget(self.cv_button)
        form_layout.addRow("CV / Resume:", cv_layout)

        self.save_button = QPushButton("Update Job" if job else "Save Job Application")
        self.save_button.clicked.connect(lambda: self.save_job(job))
        form_layout.addRow(self.save_button)

        self.content_area_layout.addWidget(form_widget)


    def save_job(self, job=None):
        if job:
            job.company = self.company_input.text()
            job.position = self.position_input.text()
            job.date_applied = self.date_input.date().toPython()
            job.status = self.status_input.currentText()
            job.notes = self.notes_input.toPlainText()
            job.description = self.description_input.toPlainText()  
            job.cover_letter_path = self.cover_letter_path.text()
            job.cv_path = self.cv_path.text()

        else:
            job = JobApplication(
                company=self.company_input.text(),
                position=self.position_input.text(),
                date_applied=self.date_input.date().toPython(),
                status=self.status_input.currentText(),
                notes=self.notes_input.toPlainText(),
                description=self.description_input.toPlainText(),
                cover_letter_path=self.cover_letter_path.text(),  # ✅ Added
                cv_path=self.cv_path.text()
            
            )
            self.session.add(job)

        self.session.commit()
        QMessageBox.information(self, "Success", "Job application saved successfully!")
        self.show_job_list()

    def delete_job(self, job_id):
        job = self.session.query(JobApplication).get(job_id)
        if job:
            self.session.delete(job)
            self.session.commit()
            QMessageBox.information(self, "Deleted", "Job application deleted successfully!")
            self.show_job_list()

    def update_status(self, job_id, new_status):
        job = self.session.query(JobApplication).get(job_id)
        if job:
            job.status = new_status
            self.session.commit()
            self.show_job_list()

    def show_job_list(self):
        self.clear_content_area()

        search_text = self.search_input.text().strip()
        query = self.session.query(JobApplication)
        if search_text:
            query = query.filter(
                (JobApplication.company.ilike(f"%{search_text}%")) |
                (JobApplication.position.ilike(f"%{search_text}%"))
            )

        jobs = query.order_by(JobApplication.date_applied.desc()).all()

        table = QTableWidget(len(jobs), 10)
        table.setHorizontalHeaderLabels([
            "Company", "Position", "Date Applied", "Status", "Notes",
            "Job Desc", "CV", "Cover Letter", "Edit", "Delete"
        ])

        header = table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(QHeaderView.Interactive)  # 🛠️ Manual resizing

        # Optional: default widths
        table.setColumnWidth(0, 160)  # Company
        table.setColumnWidth(1, 160)  # Position
        table.setColumnWidth(2, 110)  # Date
        table.setColumnWidth(3, 120)  # Status
        table.setColumnWidth(4, 200)  # Notes
        table.setColumnWidth(5, 80)   # Job Desc
        table.setColumnWidth(6, 80)   # CV
        table.setColumnWidth(7, 100)  # Cover Letter
        table.setColumnWidth(8, 60)   # Edit
        table.setColumnWidth(9, 60)   # Delete


        for row, job in enumerate(jobs):
            table.setItem(row, 0, QTableWidgetItem(job.company))
            table.setItem(row, 1, QTableWidgetItem(job.position))
            table.setItem(row, 2, QTableWidgetItem(job.date_applied.strftime("%Y-%m-%d")))

            status_combo = QComboBox()
            status_combo.addItems(["Applied", "Interview Scheduled", "Rejected", "Accepted"])
            status_combo.setCurrentText(job.status)
            status_combo.currentTextChanged.connect(self.make_status_update_callback(job.id))
            table.setCellWidget(row, 3, status_combo)

            table.setItem(row, 4, QTableWidgetItem(job.notes or ""))

            desc_button = QPushButton("📄")
            desc_button.clicked.connect(self.make_description_callback(job.description))
            table.setCellWidget(row, 5, desc_button)

            cv_button = QPushButton("📄 CV")
            cv_button.clicked.connect(self.make_open_file_callback(job.cv_path))
            table.setCellWidget(row, 6, cv_button)

            cl_button = QPushButton("📄 CL")
            cl_button.clicked.connect(self.make_open_file_callback(job.cover_letter_path))
            table.setCellWidget(row, 7, cl_button)

            edit_button = QPushButton("✏️")
            edit_button.clicked.connect(self.make_edit_callback(job))
            table.setCellWidget(row, 8, edit_button)

            delete_button = QPushButton("🗑️")
            delete_button.clicked.connect(self.make_delete_callback(job.id))
            table.setCellWidget(row, 9, delete_button)

        self.content_area_layout.addWidget(table)




    def show_dashboard(self):
        self.clear_content_area()

        jobs = self.session.query(JobApplication).all()
        total_jobs = len(jobs)
        status_counts = Counter(job.status for job in jobs)

        dashboard_container = QWidget()
        dashboard_layout = QVBoxLayout()
        dashboard_container.setLayout(dashboard_layout)
        dashboard_container.setStyleSheet("padding: 20px; background-color: #f9f9f9; border: 1px solid #ccc;")

        title = QLabel("📊 Job Application Dashboard")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        dashboard_layout.addWidget(title)

        total_label = QLabel(f"<b>Total Job Applications:</b> {total_jobs}")
        total_label.setStyleSheet("font-size: 18px; margin-bottom: 12px;")
        dashboard_layout.addWidget(total_label)

        for status, count in status_counts.items():
            status_label = QLabel(f"<b>{status}:</b> {count}")
            status_label.setStyleSheet("font-size: 16px; margin-bottom: 6px; margin-left: 10px;")
            dashboard_layout.addWidget(status_label)

        interviews_scheduled = status_counts.get("Interview Scheduled", 0)
        interviews_label = QLabel(f"<b>Interviews Scheduled:</b> {interviews_scheduled}")
        interviews_label.setStyleSheet("font-size: 16px; margin-top: 10px; margin-left: 10px;")
        dashboard_layout.addWidget(interviews_label)

        self.content_area_layout.addWidget(dashboard_container)

    def export_to_csv(self):
            path, _ = QFileDialog.getSaveFileName(self, "Save CSV", "job_applications.csv", "CSV files (*.csv)")
            if path:
                jobs = self.session.query(JobApplication).all()
                try:
                    with open(path, mode='w', newline='', encoding='utf-8') as file:
                        import csv
                        writer = csv.writer(file)
                        writer.writerow(["ID", "Company", "Position", "Date Applied", "Status", "Notes", "Description"])

                        for job in jobs:
                            writer.writerow([
                                job.id,
                                job.company,
                                job.position,
                                job.date_applied.strftime("%Y-%m-%d"),
                                job.status,
                                job.notes.replace("\n", " ") if job.notes else "",
                                job.description.replace("\n", " ") if job.description else ""
                            ])

                    QMessageBox.information(self, "Success", f"Data exported successfully to:\n{path}")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to export CSV:\n{str(e)}")

    def view_description(self, description):
                dlg = QMessageBox(self)
                dlg.setWindowTitle("Job Description")
                dlg.setText("Full Job Description:")
                dlg.setDetailedText(description or "No description provided.")
                dlg.setStandardButtons(QMessageBox.Ok)
                dlg.exec()
    def select_cover_letter(self):
            path, _ = QFileDialog.getOpenFileName(self, "Select Cover Letter", "", "PDF Files (*.pdf);;Text Files (*.txt);;All Files (*)")
            if path:
                self.cover_letter_path.setText(path)

    def select_cv(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select CV / Resume", "", "PDF Files (*.pdf);;Word Docs (*.docx);;All Files (*)")
        if path:
            self.cv_path.setText(path)

    def open_file(self, path):
        if path and os.path.exists(path):
            if platform.system() == "Darwin":  # macOS
                subprocess.call(["open", path])
            elif platform.system() == "Windows":
                os.startfile(path)
            else:  # Linux
                subprocess.call(["xdg-open", path])
        else:
            QMessageBox.warning(self, "File Not Found", f"File not found:\n{path}")

    def make_description_callback(self, desc):
        return lambda checked=False: self.view_description(desc)

    def make_open_file_callback(self, path):
        return lambda checked=False: self.open_file(path)

    def make_edit_callback(self, job):
        return lambda checked=False: self.show_add_job_form(job)

    def make_delete_callback(self, job_id):
        return lambda checked=False: self.delete_job(job_id)

    def make_status_update_callback(self, job_id):
        return lambda new_status: self.update_status(job_id, new_status)







def launch_app():
    app = QApplication(sys.argv)

    # Load QSS
    try:
        with open("gui/style.qss", "r") as f:
            style = f.read()
            app.setStyleSheet(style)
    except Exception as e:
        print("Failed to load style.qss:", e)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())
