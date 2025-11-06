# news-app-kira- fake news detection, sentiment analyser and news summerizer
Python project with Kivy interface and database viewer
# Kira App

This project is a simple Python-based application that demonstrates basic file handling, database viewing, and image display using Kivy and other Python libraries.

---

## 📂 Project Files
- **kira1.py** — Main application file (handles user interface and core logic)
- **view_db.py** — Displays data stored in the database
- **img.jpg**, **img2.jpg** — Images used for UI/background/logo

---

## 🛠️ Steps / How the Project Works

1. Run `kira1.py` to start the main application.
2. The program initializes the interface and loads the images.
3. User data or content is stored in a database (local or cloud-based).
4. Run `view_db.py` to view stored data in a formatted way.
5. The project demonstrates integration of Python scripts with images and database viewing.

## 📋 Requirements
Install the following before running:

pip install kivy
pip install kivymd
pip install newspaper3k
pip install transformers
pip install torch
pip install nltk
pip install azure-cognitiveservices-speech


| Library                            | Purpose                                                                                 |
| ---------------------------------- | --------------------------------------------------------------------------------------- |
| **kivy**                           | GUI framework for building the app interface.                                           |
| **kivymd**                         | Material Design components for Kivy (buttons, text fields, etc.).                       |
| **newspaper3k**                    | Used for extracting and summarizing news articles from URLs.                            |
| **transformers**                   | Hugging Face library for NLP tasks (sentiment analysis, fake news detection, etc.).     |
| **torch**                          | Backend library required by transformers (PyTorch).                                     |
| **nltk**                           | Natural Language Toolkit — used for text preprocessing (tokenization, stopwords, etc.). |
| **azure-cognitiveservices-speech** | Azure SDK for Text-to-Speech (TTS) integration.                                         |
