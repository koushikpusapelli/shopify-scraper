def scrape_shopify_store(website_url: str):
    # Dummy implementation for now
    return {"shop": website_url, "insights": "Sample data"}
import requests
from bs4 import BeautifulSoup
import re

def get_text(url):
    try:
        resp = requests.get(url, timeout=10)
        return resp.text if resp.status_code == 200 else None
    except:
        return None

def extract_products(website_url):
    try:
        resp = requests.get(f"{website_url}/products.json")
        if resp.status_code == 200:
            return [p["title"] for p in resp.json().get("products", [])]
    except:
        return []
    return []

def extract_social_links(soup):
    socials = {}
    links = soup.find_all("a", href=True)
    for a in links:
        href = a['href']
        if "instagram" in href:
            socials["instagram"] = href
        if "facebook" in href:
            socials["facebook"] = href
        if "tiktok" in href:
            socials["tiktok"] = href
    return socials

def extract_policies(soup):
    policies = {"privacy_policy": "", "return_policy": ""}
    for link in soup.find_all("a", href=True):
        if "privacy" in link.get("href"):
            policies["privacy_policy"] = link.get("href")
        if "return" in link.get("href") or "refund" in link.get("href"):
            policies["return_policy"] = link.get("href")
    return policies

def extract_faqs(soup):
    faqs = []
    texts = soup.get_text().split("\n")
    for i in range(len(texts)-1):
        if "?" in texts[i] and len(texts[i]) < 100:
            faqs.append({
                "question": texts[i].strip(),
                "answer": texts[i+1].strip()
            })
    return faqs[:10]

def extract_contact_info(text):
    emails = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    phones = re.findall(r"\+?[\d\s()-]{8,}", text)
    # Clean up phone numbers: remove newlines and extra spaces
    phones = [re.sub(r"\s+", " ", p).replace("\n", "").strip() for p in phones if p.strip()]
    return {"emails": list(set(emails)), "phones": list(set(phones))}

def scrape_shopify_store(website_url):
    html = get_text(website_url)
    if not html:
        return None

    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text()

    # Try to follow and extract from common subpages
    def get_subpage(path):
        url = website_url.rstrip("/") + path
        sub_html = get_text(url)
        if sub_html:
            return BeautifulSoup(sub_html, "html.parser")
        return None

    # About page
    about_soup = get_subpage("/pages/about")
    about_text = about_soup.get_text() if about_soup else ""

    # Contact page
    contact_soup = get_subpage("/pages/contact")
    contact_text = contact_soup.get_text() if contact_soup else ""


    # Privacy policy
    privacy_soup = get_subpage("/policies/privacy-policy")
    privacy_text = privacy_soup.get_text() if privacy_soup else ""
    # Clean up excessive newlines and whitespace
    privacy_text = re.sub(r"\n{2,}", "\n", privacy_text).strip()

    # Return/refund policy
    return_soup = get_subpage("/policies/refund-policy")
    return_text = return_soup.get_text() if return_soup else ""
    return_text = re.sub(r"\n{2,}", "\n", return_text).strip()

    # FAQs (try /pages/faq)
    faq_soup = get_subpage("/pages/faq")
    faqs = extract_faqs(faq_soup) if faq_soup else extract_faqs(soup)

    # Merge contact info from homepage and contact page
    contact_details = extract_contact_info(text + "\n" + contact_text)

    return {
        "brand_name": soup.title.string.strip() if soup.title else "Unknown",
        "product_catalog": extract_products(website_url),
        "hero_products": [],
        "policies": {
            "privacy_policy": privacy_text,
            "return_policy": return_text
        },
        "faqs": faqs,
        "social_handles": extract_social_links(soup),
        "contact_details": contact_details,
        "brand_about": about_text or (soup.find("meta", {"name": "description"}).get("content") if soup.find("meta", {"name": "description"}) else ""),
        "important_links": {
            "blogs": f"{website_url}/blogs",
            "order_tracking": f"{website_url}/apps/track-order",
            "contact_us": f"{website_url}/pages/contact"
        }
    }
