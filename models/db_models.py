from sqlalchemy import Column, Integer, String, Text, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ShopifyStore(Base):
    __tablename__ = "shopify_stores"
    id = Column(Integer, primary_key=True, index=True)
    website_url = Column(String(255), unique=True, nullable=False)
    brand_name = Column(String(255))
    product_catalog = Column(JSON)
    hero_products = Column(JSON)
    policies = Column(JSON)
    faqs = Column(JSON)
    social_handles = Column(JSON)
    contact_details = Column(JSON)
    brand_about = Column(Text)
    important_links = Column(JSON)
