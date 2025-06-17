from datetime import datetime

def oggi():
    return datetime.now().strftime("%Y-%m-%d")
