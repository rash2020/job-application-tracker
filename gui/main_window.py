# gui/main_window.py

import sys
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

        self.form_layout = QVBoxLayout()

        self.company_input = QLineEdit()
        self.position_input = QLineEdit()
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.status_input = QComboBox()
        self.status_input.addItems(["Applied", "Interview Scheduled", "Rejected", "Accepted"])
        self.notes_input = QTextEdit()

        if job:
            self.company_input.setText(job.company)
            self.position_input.setText(job.position)
            self.date_input.setDate(QDate(job.date_applied.year, job.date_applied.month, job.date_applied.day))
            self.status_input.setCurrentText(job.status)
            self.notes_input.setText(job.notes)

        self.save_button = QPushButton("Update Job" if job else "Save Job Application")
        self.save_button.clicked.connect(lambda: self.save_job(job))

        self.form_layout.addWidget(QLabel("Company Name:"))
        self.form_layout.addWidget(self.company_input)
        self.form_layout.addWidget(QLabel("Position:"))
        self.form_layout.addWidget(self.position_input)
        self.form_layout.addWidget(QLabel("Date Applied:"))
        self.form_layout.addWidget(self.date_input)
        self.form_layout.addWidget(QLabel("Status:"))
        self.form_layout.addWidget(self.status_input)
        self.form_layout.addWidget(QLabel("Notes:"))
        self.form_layout.addWidget(self.notes_input)
        self.form_layout.addWidget(self.save_button)

        self.content_area_layout.addLayout(self.form_layout)


    def save_job(self, job=None):
        if job:
            job.company = self.company_input.text()
            job.position = self.position_input.text()
            job.date_applied = self.date_input.date().toPython()
            job.status = self.status_input.currentText()
            job.notes = self.notes_input.toPlainText()
        else:
            job = JobApplication(
                company=self.company_input.text(),
                position=self.position_input.text(),
                date_applied=self.date_input.date().toPython(),
                status=self.status_input.currentText(),
                notes=self.notes_input.toPlainText()
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

        table = QTableWidget(len(jobs), 7)
        table.setHorizontalHeaderLabels(["Company", "Position", "Date Applied", "Status", "Notes", "Edit", "Delete"])

        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)

        for row, job in enumerate(jobs):
            table.setItem(row, 0, QTableWidgetItem(job.company))
            table.setItem(row, 1, QTableWidgetItem(job.position))
            table.setItem(row, 2, QTableWidgetItem(job.date_applied.strftime("%Y-%m-%d")))

            status_combo = QComboBox()
            status_combo.addItems(["Applied", "Interview Scheduled", "Rejected", "Accepted"])
            status_combo.setCurrentText(job.status)
            status_combo.currentTextChanged.connect(lambda new_status, job_id=job.id: self.update_status(job_id, new_status))
            table.setCellWidget(row, 3, status_combo)

            table.setItem(row, 4, QTableWidgetItem(job.notes))

            edit_button = QPushButton("✏️")
            edit_button.clicked.connect(lambda checked, j=job: self.show_add_job_form(j))
            table.setCellWidget(row, 5, edit_button)

            delete_button = QPushButton("🗑️")
            delete_button.clicked.connect(lambda checked, job_id=job.id: self.delete_job(job_id))
            table.setCellWidget(row, 6, delete_button)

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
                        writer.writerow(["ID", "Company", "Position", "Date Applied", "Status", "Notes"])
                        for job in jobs:
                            writer.writerow([
                                job.id,
                                job.company,
                                job.position,
                                job.date_applied.strftime("%Y-%m-%d"),
                                job.status,
                                job.notes.replace("\n", " ") if job.notes else ""
                            ])
                    QMessageBox.information(self, "Success", f"Data exported successfully to:\n{path}")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to export CSV:\n{str(e)}")



def launch_app():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())