import google.generativeai as genai
import os

API_KEY = 'AIzaSyBznbtPndgOqrLqQZaQjKQ_PyRnmKh6fPs'
genai.configure(api_key=API_KEY)

print("--- START MODEL LIST ---")
try:
    for m in genai.list_models():
        print(f"{m.name} | {m.supported_generation_methods}")
except Exception as e:
    print(f"ERROR: {e}")
print("--- END MODEL LIST ---")
