Shopify Scraper API
🚀 Live Demo: https://shopify-scraper-66lv.onrender.com/docs
📘 Explore the API with Swagger UI

A robust, scalable, and maintainable backend application for extracting, analyzing, and enriching data from Shopify stores. Built with FastAPI, SQLAlchemy, and Gemini LLM integration, this project is designed for extensibility and cloud deployment.

🔧 Features
Shopify Store Data Extraction
Scrapes key information from any public Shopify store, including About, Contact, Policies, and FAQ pages.

Competitor Analysis
Automatically discovers and analyzes top Shopify competitors for a given brand.

LLM-Powered Insights
Integrates Google Gemini (via google-generativeai) to summarize, clean, and enrich extracted data, providing actionable insights and improvement suggestions.

Database Storage
Persists all scraped data (main brand and competitors) in a MySQL database using SQLAlchemy ORM.

RESTful API
Exposes endpoints for scraping, insights, and data retrieval via FastAPI.

Cloud-Ready
Designed for seamless deployment to platforms like Render or Railway, with secure environment variable management.

Robust Error Handling
Handles scraping issues, database errors, and LLM failures gracefully.

🗂️ Project Structure
bash
Copy
Edit
shopify_scraper/
├── main.py                  # FastAPI app, endpoints, LLM & competitor logic
├── services/
│   └── scraper.py           # Shopify scraping logic
├── models/
│   └── db_models.py         # SQLAlchemy models
├── database/
│   └── connection.py        # DB connection/session setup
├── requirements.txt         # All dependencies
├── .env                     # Environment variables (not committed)
├── .gitignore               # Excludes sensitive files
🚀 Quick Start
Clone the repository

Install dependencies

Set up your .env file (see below)

Run the FastAPI app

bash
Copy
Edit
pip install -r requirements.txt
uvicorn main:app --reload
🔐 Environment Variables
Create a .env file in the root directory with the following keys:

ini
Copy
Edit
GEMINI_API_KEY=your_gemini_api_key
MYSQL_HOST=your_mysql_host
MYSQL_PORT=3306
MYSQL_USER=your_mysql_user
MYSQL_PASSWORD=your_mysql_password
MYSQL_DB=your_database_name
📡 API Usage
POST /fetch_insights
Request:

json
Copy
Edit
{
  "website_url": "https://brand.com"
}
Response:
Returns brand data, competitor data, and LLM-powered insights.

Explore it live at: https://shopify-scraper-66lv.onrender.com/docs

📦 Dependencies
fastapi

uvicorn

sqlalchemy

pymysql

python-dotenv

requests

google-generativeai
