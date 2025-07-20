# 📋 Job Application Tracker

A simple desktop application built with Python and PySide6 to help you keep track of your job applications.

It lets you record where you've applied, track application status, take notes, and visualize your progress with a built-in dashboard.

---

## 🧰 Features

- ✅ Add, edit, and delete job applications  
- 🗂️ Track company, position, date applied, notes, and status  
- 🔍 Search by company or job title  
- 📊 Visual dashboard showing:
  - Total applications
  - Applications per status (e.g., Applied, Interviewed)
  - Interviews scheduled  
- 🧾 Export your job applications to CSV  
- 💾 Local SQLite database (no setup required)  

---

## 🖥️ Demo

![screenshot](assets/screenshot.png) <!-- Add your own image or remove this -->

---

## 🚀 How to Run Locally

### 1. Clone the repo

```bash
git clone https://github.com/rash2020/job-application-tracker.git
cd job-application-tracker

```

### 2. Create and activate virtual environment (recommended)

```bash
python3 -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the app

```bash
python main.py
```

---

## 🛠 Tech Stack

- **Python 3.10+**  
- **PySide6** – for GUI  
- **SQLite** – local database  
- **SQLAlchemy** – ORM for database interaction  

---

## 📁 Project Structure

```bash
job-tracker/
├── data/
│   ├── database.py      # DB connection and session setup
│   ├── models.py        # SQLAlchemy JobApplication model
├── gui/
│   └── main_window.py   # Main GUI logic
├── utils/               # Helper functions (optional)
├── requirements.txt     # Python dependencies
├── main.py              # Entry point
├── assets/
│   └── screenshot.png   # Demo screenshot (optional)
└── README.md
```

---

## 📤 Export to CSV

Inside the app, use the **"Export to CSV"** option to save all job applications to a `.csv` file, which you can open in Excel, Google Sheets, or share.

---

## 📦 Packaging the App (Optional)

To create a standalone `.app` or `.exe` version :

```bash
pyinstaller --noconfirm --windowed --onedir --add-data "data:./data" main.py
```

This will generate a distributable app inside the `dist/` folder.

---

## 📄 License

MIT License – feel free to use, modify, and share!

---

## 👨‍💻 Author

Made with 💻 by Rashad Abbas

---

