
import google.generativeai as genai
import os
from dotenv import load_dotenv
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

def get_llm_analysis(data, competitors=None):
    """
    Use Gemini to summarize, clean, and enrich the extracted data.
    """
    prompt = """
You are an expert e-commerce analyst. Given the following Shopify store data, provide a concise summary, highlight key insights, and suggest any improvements or missing information. If competitors are provided, compare the main brand with its competitors.

Main Brand Data:
{brand}

Competitors Data:
{competitors}
""".format(brand=data, competitors=competitors if competitors else "None")
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"LLM analysis failed: {str(e)}"

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from services.scraper import scrape_shopify_store
import requests
import re
def get_competitor_urls(brand_url):
    """
    Simple web search for Shopify competitors using Bing search API or scraping a public list.
    For demo, we'll scrape from a public list and filter out the input brand.
    """
    try:
        # Example: Scrape from webinopoly's top 100 Shopify stores
        resp = requests.get("https://webinopoly.com/blogs/news/top-100-most-successful-shopify-stores", timeout=10)
        urls = re.findall(r'https?://[\w.-]+', resp.text)
        # Remove duplicates and the input brand
        urls = list(set([u.rstrip('/') for u in urls if brand_url not in u]))
        # Return top 3 for demo
        return urls[:3]
    except Exception:
        return []
from models.db_models import ShopifyStore, Base
from database.connection import SessionLocal, engine
import sqlalchemy.exc

app = FastAPI()

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"message": "Hello, Shopify Scraper!"}

class URLRequest(BaseModel):
    website_url: str



@app.post("/fetch_insights")
async def fetch_insights(request: URLRequest):
    db = SessionLocal()
    try:
        data = scrape_shopify_store(request.website_url)
        if data is None:
            raise HTTPException(status_code=401, detail="Invalid Shopify website or inaccessible.")

        # Store main brand
        store = db.query(ShopifyStore).filter(ShopifyStore.website_url == request.website_url).first()
        if store:
            for key, value in data.items():
                setattr(store, key, value)
        else:
            store = ShopifyStore(website_url=request.website_url, **data)
            db.add(store)
        db.commit()
        db.refresh(store)

        # BONUS: Get competitors and their insights
        competitors = []
        for comp_url in get_competitor_urls(request.website_url):
            comp_data = scrape_shopify_store(comp_url)
            if comp_data:
                competitors.append({"website_url": comp_url, **comp_data})
                # Store competitor in DB if not exists
                comp_store = db.query(ShopifyStore).filter(ShopifyStore.website_url == comp_url).first()
                if not comp_store:
                    db.add(ShopifyStore(website_url=comp_url, **comp_data))
        db.commit()

        llm_analysis = get_llm_analysis(data, competitors)
        return {
            "llm_analysis": llm_analysis,
            "brand": data,
            "competitors": competitors
        }
    except sqlalchemy.exc.SQLAlchemyError as db_err:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"DB Error: {str(db_err)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()
