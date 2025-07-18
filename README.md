#Shopify Scraper API

A robust, scalable, and maintainable backend application for extracting, analyzing, and enriching data from Shopify stores. Built with FastAPI, SQLAlchemy, and Gemini LLM integration, this project is designed for extensibility and cloud deployment.

#Features

- **Shopify Store Data Extraction**: Scrapes key information from any public Shopify store, including About, Contact, Policies, and FAQ pages.
- **Competitor Analysis**: Automatically discovers and analyzes top Shopify competitors for a given brand.
- **LLM-Powered Insights**: Integrates Google Gemini (via `google-generativeai`) to summarize, clean, and enrich extracted data, providing actionable insights and improvement suggestions.
- **Database Storage**: Persists all scraped data (main brand and competitors) in a MySQL database using SQLAlchemy ORM.
- **RESTful API**: Exposes endpoints for scraping, insights, and data retrieval via FastAPI.
- **Cloud-Ready**: Designed for seamless deployment to platforms like Railway, with secure environment variable management.
- **Error Handling**: Robust error handling for scraping, database, and LLM operations.

#Project Structure

```
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
```

#Quick Start

1. **Clone the repository**
2. **Install dependencies**
3. **Set up your `.env` file** (see below)
4. **Run the FastAPI app**

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

#Environment Variables

Create a `.env` file in the root directory with the following keys:

```
GEMINI_API_KEY=your_gemini_api_key
MYSQL_HOST=your_mysql_host
MYSQL_PORT=3306
MYSQL_USER=your_mysql_user
MYSQL_PASSWORD=your_mysql_password
MYSQL_DB=your_database_name
```

#API Usage

- **POST `/fetch_insights`**
    - Request: `{ "website_url": "https://brand.com" }`
    - Response: LLM-powered analysis, brand data, and competitor data.

#Dependencies

- fastapi
- uvicorn
- sqlalchemy
- pymysql
- python-dotenv
- requests
- google-generativeai
--------------------------------------------
