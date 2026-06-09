# AI-Driven Customer Analytics and Personalization Platform

## Live Website

🔗 https://ai-driven-customer-analytics-and-cmy8.onrender.com

---

# Project Overview

The AI-Driven Customer Analytics and Personalization Platform is a full-stack Machine Learning web application built using Flask, Pandas, Scikit-learn, Bootstrap, JavaScript, and Chart.js.

The platform helps businesses analyze customer behavior data, generate insights, segment customers, predict future purchases, and create personalized recommendations through an interactive dashboard.

This project is designed for academic, portfolio, and demonstration purposes.

---

# Features

## Data Upload

* Upload customer datasets in:

  * Excel (`.xlsx`)
  * JSON (`.json`)

## Data Validation

* Validates required customer schema
* Detects missing columns
* Handles invalid datasets safely

## Data Cleaning & Preprocessing

* Removes duplicate customers
* Handles missing values
* Standardizes formats
* Parses dates and numeric values

## Descriptive Analytics

* Total customers
* Total spending
* Average spending
* Purchase frequency analysis
* Category distribution
* Location distribution
* Missing value analysis

## Customer Segmentation

* KMeans clustering
* Customer grouping:

  * Low Value
  * Medium Value
  * High Value

## Purchase Prediction

* Predicts future customer purchases
* Uses Decision Tree Classifier
* Includes:

  * Accuracy
  * Precision
  * Recall
  * F1 Score

## Recommendation Engine

* Rule-based personalized recommendations
* Campaign targeting suggestions
* Customer retention strategies

## Interactive Dashboard

* KPI cards
* Charts
* Tables
* Responsive UI
* Section navigation

## Export System

* Export reports as:

  * JSON
  * Excel

---

# Tech Stack

## Backend

* Flask
* Python

## Data Processing

* Pandas
* NumPy

## Machine Learning

* Scikit-learn

## Frontend

* HTML
* CSS
* Bootstrap
* JavaScript
* Chart.js

---

# Machine Learning Algorithms Used

## KMeans Clustering

Used for customer segmentation based on:

* Total Spending
* Purchase Frequency
* Age

### Why KMeans?

* Lightweight
* Fast
* Easy to visualize
* Suitable for academic projects
* Effective for customer grouping

---

## Decision Tree Classifier

Used for predicting:

* `will_purchase_next_month`

### Why Decision Tree?

* Simple and interpretable
* Handles small datasets well
* Deterministic results
* Easy for assignment demonstration

---

# Project Workflow

```text id="m88u3f"
Upload Dataset
       ↓
Validate Dataset
       ↓
Clean & Preprocess Data
       ↓
Generate Analytics
       ↓
Customer Segmentation
       ↓
Purchase Prediction
       ↓
Generate Recommendations
       ↓
Display Dashboard
       ↓
Export Reports
```

---

# Project Structure

```text id="q7b2rv"
AI-driven/
│
├── app.py
├── requirements.txt
├── README.md
│
├── config/
│   └── settings.py
│
├── routes/
│   ├── upload_routes.py
│   ├── dashboard_routes.py
│   └── export_routes.py
│
├── src/
│   ├── file_handler.py
│   ├── data_loader.py
│   ├── data_validator.py
│   ├── data_cleaner.py
│   ├── analytics.py
│   ├── segmentation.py
│   ├── prediction.py
│   ├── recommendation.py
│   └── exporter.py
│
├── templates/
│   ├── base.html
│   ├── upload.html
│   └── dashboard.html
│
├── static/
│   ├── css/
│   └── js/
│
├── data/
│   ├── uploads/
│   ├── processed/
│   └── exports/
│
└── models/
```

---

# Dataset Schema

Required columns:

| Column Name        | Description                 |
| ------------------ | --------------------------- |
| customer_id        | Unique customer identifier  |
| age                | Customer age                |
| gender             | Customer gender             |
| location           | Customer city/location      |
| purchase_frequency | Number of purchases         |
| total_spending     | Total spending amount       |
| preferred_category | Preferred shopping category |
| last_purchase_date | Last purchase date          |

---

# Sample Dataset

```json id="rq5f1g"
[
  {
    "customer_id": "C001",
    "age": 28,
    "gender": "Female",
    "location": "Delhi",
    "purchase_frequency": 5,
    "total_spending": 12000,
    "preferred_category": "Electronics",
    "last_purchase_date": "2026-05-20"
  },
  {
    "customer_id": "C002",
    "age": 35,
    "gender": "Male",
    "location": "Mumbai",
    "purchase_frequency": 2,
    "total_spending": 4500,
    "preferred_category": "Fashion",
    "last_purchase_date": "2026-05-10"
  }
]
```

---

# Installation

## Clone Repository

```bash id="z6m67f"
git clone https://github.com/MiriyamRevathi/AI-Driven_Customer_Analytics_and_Personalization_Platform.git
```

---

## Open Project Folder

```bash id="1qj3ec"
cd AI-Driven_Customer_Analytics_and_Personalization_Platform
```

---

## Install Dependencies

```bash id="jcv5qa"
pip install -r requirements.txt
```

---

# Run Application

```bash id="v2kztm"
python app.py
```

Open browser:

```text id="cr25ij"
http://127.0.0.1:5000
```

---

# Available Endpoints

| Endpoint        | Method   | Description                  |
| --------------- | -------- | ---------------------------- |
| `/upload`       | GET/POST | Upload dataset               |
| `/dashboard`    | GET      | Dashboard UI                 |
| `/analyze`      | GET      | Descriptive analytics        |
| `/segment`      | GET      | Customer segmentation        |
| `/predict`      | GET      | Purchase prediction          |
| `/recommend`    | GET      | Personalized recommendations |
| `/export/json`  | GET      | Export JSON report           |
| `/export/excel` | GET      | Export Excel report          |

---

# Dashboard Modules

## Analytics Dashboard

* KPI cards
* Charts
* Distribution analysis
* Customer insights

## Segmentation Dashboard

* Customer cluster grouping
* High/Medium/Low value customers

## Prediction Dashboard

* Purchase prediction
* Model metrics
* Prediction probabilities

## Recommendation Dashboard

* Personalized campaign suggestions
* Retention strategies
* Upsell opportunities

---

# Export Reports

Supported formats:

* JSON
* Excel

Excel report sheets:

* Analytics
* Segments
* Predictions
* Recommendations

---

# Demo Workflow

1. Open the website
2. Upload `.xlsx` or `.json` customer dataset
3. Validate and clean dataset
4. View analytics dashboard
5. View segmentation results
6. View prediction results
7. View recommendation results
8. Export reports

---

# Error Handling Features

* Invalid file detection
* Missing column validation
* Small dataset protection
* Safe missing value handling
* Deterministic ML behavior
* Graceful dashboard errors

---

# Future Improvements

* Authentication system
* Database integration
* PDF exports
* Advanced recommendation engine
* Cloud deployment
* Deep learning models
* Real-time analytics
* User management system

---

# Technologies Used

* Flask
* Pandas
* NumPy
* Scikit-learn
* Bootstrap
* HTML
* CSS
* JavaScript
* Chart.js

---

# Author

Miriyam Revathi

---

# License

This project is developed for academic and educational purposes.

# Final Notes

This project demonstrates:

* Full-stack development
* Machine Learning integration
* Data preprocessing
* Customer analytics
* Business intelligence dashboard design
* Rule-based recommendation systems
* Interactive frontend integration

