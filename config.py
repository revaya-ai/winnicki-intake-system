"""Winnicki Digital - Business Configuration"""

COMPANY_INFO = {
    "name": "Winnicki Digital",
    "website": "https://www.winnickidigital.com",
    "contact_email": "shannon@winnickidigital.com",
    "services": ["Website Design", "SEO", "AI Automation", "Voice Agents"],
    "platforms": ["Wix", "Shopify", "HighLevel", "Webflow"]
}

WEBSITE_PACKAGES = {
    "single_page": {
        "name": "Single Page Website",
        "base_price": 700,
        "pages": 1,
        "additional_page_cost": 300,
        "timeline": "1-2 weeks",
        "features": ["Mobile Responsive", "Image Gallery", "Lead Capture Form", "Embedded Video", "Social Share", "You Own The Website"]
    },
    "small": {
        "name": "Small Website",
        "base_price": 1999,
        "pages": 5,
        "additional_page_cost": 300,
        "blog_addon": 500,
        "training_rate": 70,
        "timeline": "2-3 weeks",
        "features": ["Up to 5 Pages", "Mobile Responsive", "e-Commerce (lite)", "Ticketing System", "Google Search Console", "You Own The Website"]
    },
    "large": {
        "name": "Large Website",
        "base_price": 3999,
        "pages": 15,
        "additional_page_cost": 200,
        "blog_addon": 400,
        "training_rate": 50,
        "timeline": "4-6 weeks",
        "features": ["Up to 15 Pages", "Full e-Commerce", "Ticketing System", "Google Search Console", "You Own The Website"]
    }
}

ADDITIONAL_SERVICES = {
    "seo": {"name": "SEO Services", "pricing": "Custom", "timeline": "3-6 months"},
    "voice_agent": {"name": "AI Voice Agent", "pricing": "$2000-5000 setup", "timeline": "2-3 weeks"},
    "ai_automation": {"name": "AI Automation", "hourly_rate": 150, "timeline": "Varies"}
}

EMAIL_CONFIG = {
    "recipient": "shannon@winnickidigital.com",
    "from_email": "system@winnickidigital.com"
}

SLACK_CONFIG = {
    "channel": "wd-leads",
    "webhook_url": "ENV_VAR"
}

GOOGLE_DRIVE_CONFIG = {
    "folder_name": "Winnicki Digital Agent Proposals"
}
