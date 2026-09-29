import os
import django
import sys
import requests

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'photography_project.settings')
django.setup()

from main.models import ChatbotFAQ

BASE_URL = 'http://127.0.0.1:8080/ai-chat/'
HOME_URL = 'http://127.0.0.1:8080/'

session = requests.Session()
session.get(HOME_URL)
csrftoken = session.cookies.get('csrftoken', '')

headers = {
    'Content-Type': 'application/json',
    'X-CSRFToken': csrftoken,
    'Referer': HOME_URL
}

def ask_ai(question):
    print(f"\nAsking: {question}")
    resp = session.post(BASE_URL, json={'message': question, 'history': []}, headers=headers)
    return resp.json().get('reply', '')

if __name__ == "__main__":
    print("--- Testing DB Synchronization ---")
    
    # 1. Ask before adding
    q = "What is your unique test code for today?"
    print(f"Before DB Update: {ask_ai(q)}")
    
    # 2. Add to DB
    print("\nAdding record to ChatbotFAQ via Django ORM...")
    faq = ChatbotFAQ.objects.create(question="What is your unique test code for today?", answer="My unique test code is ALPHA-9988-BRAVO.")
    
    # 3. Ask after adding
    try:
        reply = ask_ai(q)
        print(f"After DB Update: {reply}")
        if "ALPHA" in reply:
            print("Status: \033[92mPASS\033[0m - AI is querying the DB dynamically.")
        else:
            print("Status: \033[91mFAIL\033[0m")
    finally:
        faq.delete()
        print("Cleaned up test FAQ.")
