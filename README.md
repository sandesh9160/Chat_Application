# 🚀 Django Chat App

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.x-green.svg)](https://www.djangoproject.com/)
[![Websockets](https://img.shields.io/badge/WebSockets-Enabled-brightgreen)](#)

---

<p align="center">
  <img src="https://img.icons8.com/color/96/000000/weixing.png" width="80" alt="Chat App Icon"/>
</p>

<h2 align="center">A modern, WhatsApp-like real-time chat app built with Django & Channels</h2>

---

## ✨ Features

- 💬 **Real-time chat** with WebSockets (Django Channels)
- 🔒 **User authentication** (login/register/logout)
- 📎 **Send & receive images (JPG/PNG) and PDF attachments**
- 🧵 **WhatsApp-style reply threading** (click to scroll to original message)
- 🏷️ **@Mentions** with autocomplete
- 🖼️ **Large preview page** for images & PDFs with download option
- 📱 **Responsive, mobile-friendly UI** (Bootstrap)
- 🛡️ **Secure file handling & download**

---

## 📸 Demo

<p align="center">
  <!-- Replace with your own GIF or screenshot -->
  <img src="https://user-images.githubusercontent.com/placeholder/demo.gif" width="600" alt="Chat Demo"/>
</p>

---

## 🛠️ Getting Started

### Prerequisites
- Python 3.8+
- pip
- (Recommended) Virtualenv

### Installation

```bash
# 1. Clone the repository
$ git clone <your-repo-url>
$ cd django_chat

# 2. Create and activate a virtual environment
$ python -m venv venv
$ source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
$ pip install -r requirements.txt

# 4. Apply migrations
$ python manage.py migrate

# 5. (Optional) Create a superuser
$ python manage.py createsuperuser

# 6. Run the development server
$ daphne -b 0.0.0.0 -p 8000 django_chat.asgi:application
# or
$ python manage.py runserver
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

---

## 🗂️ Project Structure

```text
django_chat/
  chat/                # Main chat app
    templates/         # HTML templates
    static/            # Static files (CSS, JS)
    models.py          # Message and attachment models
    consumers.py       # WebSocket consumers
    views.py           # Django views
    ...
  django_chat/         # Project settings
  media/               # Uploaded attachments
  static/              # Static files root
  requirements.txt     # Python dependencies
  manage.py            # Django management script
```

---

## 🚀 Deployment
- For production, use **Daphne** or **Uvicorn** with a proper ASGI server setup.
- Configure static/media file serving and secure secret keys.

---

## 🙏 Credits
- [Bootstrap](https://getbootstrap.com/), [Bootstrap Icons](https://icons.getbootstrap.com/)
- [Django](https://www.djangoproject.com/), [Django Channels](https://channels.readthedocs.io/)

---

## 📄 License

This project is licensed under the MIT License.

---

<p align="center">
  <b>Made with ❤️ using Django & Channels</b>
</p> 