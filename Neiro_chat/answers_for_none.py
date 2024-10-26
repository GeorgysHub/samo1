from docx import Document
import json

default_responses = {}

files = {
    "Audio": {
        "path": "./Neiro_chat/dsd/Audio.docx",
        "keywords": ["audio", "sound", "speaker", "volume", "microphone", "mute", "headphones", "voice", "recording", "noise cancellation", "echo", "voice chat", "distortion", "clarity", "frequency", "output", "input", "bluetooth", "pairing", "balance", "acoustic", "quality", "enhancement"]
    },
    "BATCH": {
        "path": "./Neiro_chat/dsd/BATCH.docx",
        "keywords": ["batch", "automation", "task", "determination", "inventory", "process", "production", "sales", "order", "warehouse", "management", "selection", "criteria", "analysis", "availability", "log", "strategy", "search", "characteristic", "classification", "quantity", "sorting", "split", "stock", "occupy", "release", "condition", "transaction code"]
    },
    "Camera": {
        "path": "./Neiro_chat/dsd/Camera.docx",
        "keywords": ["camera", "webcam", "video", "image", "picture", "resolution", "lens", "live feed", "streaming", "snapshot", "zoom", "focus", "clarity", "lighting", "sharpness", "framerate", "privacy", "angle", "brightness", "position", "exposure", "white balance", "capture"]
    },
    "Cleaning PC Cooler": {
        "path": "./Neiro_chat/dsd/Cleaning PC Cooler.docx",
        "keywords": ["cooler", "cleaning", "fan", "temperature", "overheating", "dust", "performance", "noise", "thermal paste", "heat dissipation", "airflow", "cooling system", "PC maintenance", "CPU fan", "ventilation", "clogged fan", "heating", "compressor", "hardware", "clean", "brush"]
    },
    "Configuring macros in MICROSOFT EXCEL": {
        "path": "./Neiro_chat/dsd/Configuring macros in MICROSOFT EXCEL.docx",
        "keywords": ["excel", "macros", "configuration", "automation", "spreadsheet", "formulas", "vba", "scripting", "data entry", "macro recording", "code editor", "conditional formatting", "functions", "pivot tables", "loop", "sheet", "shortcut", "developer tab", "worksheet", "cells"]
    },
    "Connect printer": {
        "path": "./Neiro_chat/dsd/Connect printer.docx",
        "keywords": ["printer", "connect", "setup", "printing", "driver", "install", "wireless", "print queue", "paper jam", "configuration", "network printer", "USB", "troubleshoot", "offline", "connectivity", "ink", "cartridge", "permissions", "scanner", "connection"]
    },
    "Connecting VPN": {
        "path": "./Neiro_chat/dsd/Connecting VPN.DOCX",
        "keywords": ["vpn", "connection", "remote access", "secure", "login", "encryption", "network", "firewall", "access", "IPsec", "authentication", "protocol", "vpn client", "SSL", "configuration", "tunneling", "connectivity", "network security", "private network"]
    },
    "Mouse settings": {
        "path": "./Neiro_chat/dsd/Mouse settings.docx",
        "keywords": ["mouse", "settings", "cursor", "pointer", "sensitivity", "speed", "click", "tracking", "scroll", "double-click", "pointer speed", "dpi adjustment", "USB", "wireless mouse", "driver", "tracking", "gaming mouse"]
    },
    "Network connection": {
        "path": "./Neiro_chat/dsd/Network connection.docx",
        "keywords": ["network", "connection", "internet", "ethernet", "wifi", "LAN", "router", "modem", "network settings", "reconnect", "signal", "bandwidth", "network adapter", "IP address", "Wi-Fi issues", "connectivity", "speed test"]
    },
    "Outlook connection fix": {
        "path": "./Neiro_chat/dsd/Otlook connection fix.docx",
        "keywords": ["outlook", "email", "connection", "fix", "send", "receive", "SMTP", "account", "sync", "server settings", "exchange", "inbox", "password", "login", "IMAP", "outlook error", "connectivity", "mail setup", "troubleshooting"]
    },
    "Password": {
        "path": "./Neiro_chat/dsd/Password.docx",
        "keywords": ["password", "reset", "security", "credentials", "account", "password policy", "password change", "forgot password", "secure password", "authentication", "recovery", "password requirements", "login issue", "account recovery", "security question", "password expiration"]
    },
    "Firewall parameters": {
        "path": "./Neiro_chat/dsd/Firewall parameters.docx",
        "keywords": ["firewall", "security", "network", "access", "protection", "data", "rules", "traffic", "firewall settings", "block", "inbound", "outbound", "ports", "firewall rules", "malware protection", "antivirus", "logging", "firewall policy", "filtering"]
    },
    "License upgrade": {
        "path": "./Neiro_chat/dsd/License upgrade.docx",
        "keywords": ["license", "activation", "key", "serial number", "subscription", "purchase", "renewal", "product key", "Windows activation", "digital license", "software license", "update", "validation", "license manager", "upgrade procedure"]
    },
    "Microphone": {
        "path": "./Neiro_chat/dsd/Microphone.docx",
        "keywords": ["microphone", "audio", "recording", "input", "volume", "permissions", "settings", "access", "Windows 11", "microphone access", "headset", "troubleshoot", "webcam", "privacy", "sound quality", "gain", "calibration", "mic check", "microphone boost"]
    },
    "Performance": {
        "path": "./Neiro_chat/dsd/Performance.docx",
        "keywords": ["performance", "speed", "optimization", "system", "memory", "cpu", "efficiency", "lag", "slow", "boost", "performance tuning", "disk space", "RAM", "processor", "application load", "speed up", "freeze", "crash", "resource usage", "background apps", "windows update", "optional updates", "settings", "check for updates"]
    },
    "PR": {
        "path": "./Neiro_chat/dsd/PR.DOCX",
        "keywords": ["public relations", "PR", "communication", "media", "press release", "marketing", "campaign", "outreach", "advertisement", "branding", "social media", "publicity", "announcement", "promotion", "target audience", "media release", "event", "press contact", "strategy", "purchase requisition", "SAP", "procurement", "inventory", "account assignment"]
    },
    "Printer": {
        "path": "./Neiro_chat/dsd/Printer.docx",
        "keywords": ["printer", "printing", "paper", "ink", "cartridge", "error", "jam", "tray", "print quality", "spooler", "duplex", "toner", "refill", "alignment", "network printer", "test page", "paper tray", "toner level", "print settings", "printing delay", "connectivity"]
    },
    "Program installation": {
        "path": "./Neiro_chat/dsd/Program installation.docx",
        "keywords": ["program", "installation", "software", "setup", "download", "error", "license", "requirements", "installation failed", "setup guide", "install wizard", "uninstall", "repair", "path", "registry", "configuration", "install package", "disk space", "installer", "install mode"]
    },
    "Screen Resolution": {
        "path": "./Neiro_chat/dsd/Screen Resolution.docx",
        "keywords": ["screen", "resolution", "display", "monitor", "dpi", "brightness", "contrast", "scaling", "color depth", "refresh rate", "aspect ratio", "adjustment", "resolution settings", "screen size", "orientation", "primary monitor", "dual display", "fullscreen", "projector", "sharpness"]
    },
    "Software upgrade": {
        "path": "./Neiro_chat/dsd/Software upgrade.docx",
        "keywords": ["software", "upgrade", "update", "version", "installation", "patch", "release", "features", "enhancement", "compatibility", "new features", "functionality", "system update", "software release", "stability", "bug fix", "update guide", "installation error"]
    },
    "Spam filter": {
        "path": "./Neiro_chat/dsd/Spam filter.docx",
        "keywords": ["spam", "filter", "email", "junk", "block", "settings", "protection", "ads", "spam settings", "unwanted email", "blacklist", "whitelist", "email filter", "phishing", "spam protection"]
    }
}


def extract_text_from_page(doc, start_page=3):
    text = ""
    current_page = 1
    for paragraph in doc.paragraphs:
        if current_page >= start_page:
            line = paragraph.text.strip()
            if line and not any(keyword in line.upper() for keyword in ['VERSION', 'INTRODUCTORY', 'GOALS']):
                text += line + "\n"
        if paragraph.text == "":
            current_page += 1
    return text

for category, info in files.items():
    doc = Document(info["path"])
    text = extract_text_from_page(doc, start_page=3)
    default_responses[category] = {
        "text": text,
        "keywords": info["keywords"]
    }

with open('./Neiro_chat/default_responses.json', 'w', encoding='utf-8') as f:
    json.dump(default_responses, f, ensure_ascii=False, indent=4)

def get_default_response(category_name):
    with open('./Neiro_chat/default_responses.json', 'r', encoding='utf-8') as f:
        default_responses = json.load(f)
    return default_responses.get(category_name, {}).get("text", "Ответ для этой категории отсутствует")

def find_response_by_keywords(query):
    with open('./Neiro_chat/default_responses.json', 'r', encoding='utf-8') as f:
        default_responses = json.load(f)

    query = query.lower()
    keyword_scores = {}

    for category, info in default_responses.items():
        query_score = sum(query.count(keyword) for keyword in info["keywords"])

        if query_score > 0:
            keyword_scores[category] = query_score

    if keyword_scores:
        best_category = max(keyword_scores, key=keyword_scores.get)
        return default_responses[best_category]["text"]

    return "Sorry, no suitable instruction was found."