## this project is running on render's free plan , so when you first come inside this site it just will take a bit of your time , but dont worry about that , all is work,just because the limit of free plan

# 🚗 New Driver Help — Driver Service Platform

A full-stack web application to support and manage driver services across Kazakhstan. The platform allows users to find drivers based on specific filters (e.g., region, experience, car type) and provides an admin panel for managing all data.

## 🌟 Features

### 👤 User Side:
- 🔍 Search and filter drivers by region, experience, and service type.
- 📱 Responsive and easy-to-use interface.
- 📂 View driver profiles with service information and contact details.

### 🛠️ Admin Panel:
- 📋 View, add, edit, and delete driver records.
- 📊 Dashboard to monitor total drivers and regions served.
- 🔐 Secure login for administrators.

### 📍 Future Additions:
- 📈 Driver performance ratings.
- 🗺️ Map-based search.
- 📅 Booking system integration.
- 🌐 Multi-language support (Kazakh, Russian, English).

## 💻 Tech Stack

| Layer         | Tech                                      |
|---------------|-------------------------------------------|
| Frontend      | HTML, CSS, JavaScript (Bootstrap, jQuery) |
| Backend       | Python (Flask)                            |
| Database      | SQLite (can be upgraded to PostgreSQL)    |
| Admin Panel   | Flask Admin + Custom Styling              |
| Deployment    | Localhost (can be hosted on Heroku/VPS)   |

## 🚀 Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/nurbek18/new_driver_help.git
cd new_driver_help
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the app
```bash
python app.py
```

Open your browser and go to:  
`http://127.0.0.1:5000/` – for the user interface  
`http://127.0.0.1:5000/admin` – for the admin panel

## 📦 Folder Structure

```
new_driver_help/
│
├── static/             # CSS, JS, images
├── templates/          # HTML templates (Jinja2)
├── app.py              # Main application
├── models.py           # Database models
├── config.py           # Configuration file
├── requirements.txt    # Python dependencies
└── README.md           # Project description
```

## 🛣️ Project Goal

This platform is designed to help people across Kazakhstan easily find and request driver services. It can also be scaled for other logistics-related services such as couriers or taxi aggregators.

## 🤝 Contributing

Feel free to fork the repo and suggest improvements via pull requests. Any ideas or feedback are welcome!

## 📧 Contact

Made with ❤️ by **Nurbek**  
Email: dohdyrbeknurbek@gmail.com  
Telegram: @D_Nurbek_1314
