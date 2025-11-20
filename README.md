# WhatsApp Product Review Collector

A full-stack application that collects product reviews via WhatsApp messages and displays them in a real-time web dashboard.

##  Features

- **WhatsApp Integration**: Collect reviews through natural conversations
- **Real-time Dashboard**: View all reviews in a clean, responsive interface
- **RESTful API**: Complete backend API for managing reviews
- **Modern Stack**: FastAPI + React + SQLite

##  Tech Stack

**Backend:** FastAPI, SQLite, Twilio (WhatsApp), Python  
**Frontend:** React, Vite, Axios, CSS3

##  Prerequisites

Before running this project, ensure you have installed:

- **Python 3.8+**
- **Node.js 16+**
- **npm** (comes with Node.js)

##  Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/nehachoudhary0731/WhatsApp-Review-Collector.git
cd WhatsApp-Review-Collector
```
 2. Backend Setup (FastAPI)
1.Navigate to Backend Directory
cd backend
- Windows
python -m venv venv
venv\Scripts\activate
- Mac/Linux
python3 -m venv venv
source venv/bin/activate

 2.Install Dependencies
  
pip install -r requirements.txt

3.Run the Backend Server

uvicorn app.main:app --reload --port 8000

## Frontend Setup (React)
1.Open New Terminal & Navigate to Frontend 

(cd frontend)

2.Install Dependencies

npm install

3.Start Development Server

npm run dev
