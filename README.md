
# 🚗 DriveSafeNow — **Seamless Designated Driver Platform** 

> This project is running on Render's free plan. When visiting the site for the first time, it might take a few seconds to load. Please be patient – everything works fine, it's just the free-tier limitation. ✅

## 📊 Project Overview

**DriveSafeNow** is a full-stack multilingual web application aimed at helping users find reliable designated drivers after drinking and allowing drivers to offer their services. Built for Kazakhstan but scalable globally.

* 🌐 Supports  **Kazakh** ,  **Russian** ,  **English** , and **Chinese**
* ✨ Allows users to **request drivers** and drivers to **register themselves**
* ⚖️ Admin dashboard for complete management
* 📅 Future updates: rating, booking, maps, and more

---

## 🌟 Features

### 👤 User Side

* 🔍 Search and filter drivers by region, experience, service type
* 📱 Fully responsive, mobile-ready interface
* 📂 View driver profiles with contact and service info

### 🛠️ Driver Side

* 📅 Easy registration to offer your driving services
* ✅ Multi-language form support

### 🔑 Admin Panel

* 📄 Add / Edit / Delete driver entries
* 📊 Dashboard with statistics (total drivers, regions, etc.)
* 🔐 Secure login access

### 🌍 Future Additions

* ⬆️ Driver rating system
* 📍 Map-based UI
* 📆 Booking and scheduling system

---

## 💻 Tech Stack

| Layer       | Tech                                      |
| ----------- | ----------------------------------------- |
| Frontend    | HTML, CSS, JavaScript (Bootstrap, jQuery) |
| Backend     | Python (Flask)                            |
| Database    | SQLite (can be upgraded to PostgreSQL)    |
| Admin Panel | Flask-Admin + Custom Styling              |
| Deployment  | Render (Free plan)                        |

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/nurbek18/new_driver_help.git
cd new_driver_help
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the App

```bash
python main.py
```

### 4. Visit in Browser

* `http://127.0.0.1:5000/` — User side
* `http://127.0.0.1:5000/admin` — Admin dashboard

---

## 📆 Folder Structure

```
new_driver_help/
├── static/             # CSS, JS, images
├── templates/          # HTML templates (Jinja2)
├── app.py              # Main application
├── main.py             # Project entry point
├── models.py           # Database models
├── config.py           # App configuration
├── requirements.txt    # Python dependencies
└── README.md           # Project info
```

---

## 🛍️ Project Goal

This platform is tailored to help citizens in Kazakhstan request or offer safe driving services, especially for those who cannot drive due to alcohol consumption. It can later scale to serve courier, taxi, or delivery sectors.

---

## 🤝 Contributing

Pull requests are welcome! Fork the repo and suggest features, bug fixes, or improvements. Let’s build together!

---

## 📧 Contact

Made with ❤️ by **Nurbek**

* Email: `dohdyrbeknurbek@gmail.com`
* Telegram: [@D_Nurbek_1314](https://t.me/D_Nurbek_1314)
* Render Site: [https://drivesafenow.onrender.com](https://drivesafenow.onrender.com/)
