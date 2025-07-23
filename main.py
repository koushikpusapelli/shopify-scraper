import uvicorn

import os
import json
import requests
import re
import sqlalchemy.exc
import google.generativeai as genai
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from services.scraper import scrape_shopify_store
from models.db_models import ShopifyStore, Base
from database.connection import SessionLocal, engine

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)



# Create tables if not exist
Base.metadata.create_all(bind=engine)

class URLRequest(BaseModel):
    website_url: str
from fastapi.responses import RedirectResponse

@app.get("/")
def root():
    return RedirectResponse(url="/docs")
#@app.get("/")
#def read_root():
 #   return {"message": "Hello, Shopify Scraper!"}

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

def get_competitor_urls(brand_url):
    """
    Scrape from public list of top Shopify stores, exclude the input brand.
    """
    try:
        resp = requests.get("https://webinopoly.com/blogs/news/top-100-most-successful-shopify-stores", timeout=10)
        urls = re.findall(r'https?://[\w.-]+', resp.text)
        urls = list(set([u.rstrip('/') for u in urls if brand_url not in u]))
        return urls[:3]  # Return top 3
    except Exception:
        return []

@app.post("/fetch_insights")
async def fetch_insights(request: URLRequest):
    db = SessionLocal()
    try:
        data = scrape_shopify_store(request.website_url)
        if data is None:
            raise HTTPException(status_code=401, detail="Invalid Shopify website or inaccessible.")

        # Serialize JSON-compatible fields
        store_data = ShopifyStore(
            website_url=request.website_url,
            brand_name=data.get("brand_name"),
            product_catalog=json.dumps(data.get("product_catalog")),
            hero_products=json.dumps(data.get("hero_products")),
            policies=json.dumps(data.get("policies")),
            faqs=json.dumps(data.get("faqs")),
            social_handles=json.dumps(data.get("social_handles")),
            contact_details=json.dumps(data.get("contact_details")),
            brand_about=data.get("brand_about"),
            important_links=json.dumps(data.get("important_links")),
        )

        # Check if brand already exists
        existing = db.query(ShopifyStore).filter(ShopifyStore.website_url == request.website_url).first()
        if existing:
            for key, value in store_data.__dict__.items():
                if key != "_sa_instance_state":
                    setattr(existing, key, value)
        else:
            db.add(store_data)

        # Process competitors
        competitors = []
        for comp_url in get_competitor_urls(request.website_url):
            comp_data = scrape_shopify_store(comp_url)
            if comp_data:
                competitors.append({"website_url": comp_url, **comp_data})
                comp_existing = db.query(ShopifyStore).filter(ShopifyStore.website_url == comp_url).first()
                if not comp_existing:
                    db.add(ShopifyStore(
                        website_url=comp_url,
                        brand_name=comp_data.get("brand_name"),
                        product_catalog=json.dumps(comp_data.get("product_catalog")),
                        hero_products=json.dumps(comp_data.get("hero_products")),
                        policies=json.dumps(comp_data.get("policies")),
                        faqs=json.dumps(comp_data.get("faqs")),
                        social_handles=json.dumps(comp_data.get("social_handles")),
                        contact_details=json.dumps(comp_data.get("contact_details")),
                        brand_about=comp_data.get("brand_about"),
                        important_links=json.dumps(comp_data.get("important_links")),
                    ))
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

# Entry point for Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)

