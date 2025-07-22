from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ShopifyStore(Base):
    __tablename__ = "shopify_stores"
    id = Column(Integer, primary_key=True, index=True)
    website_url = Column(String(255), unique=True, nullable=False)
    brand_name = Column(String(255))
    
    # Changed JSON to Text for compatibility
    product_catalog = Column(Text)
    hero_products = Column(Text)
    policies = Column(Text)
    faqs = Column(Text)
    social_handles = Column(Text)
    contact_details = Column(Text)
    brand_about = Column(Text)
    important_links = Column(Text)
