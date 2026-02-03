import sys
try:
    from google import genai
    print("SUCCESS: Google GenAI Imported")
    print(f"File: {genai.__file__}")
except ImportError as e:
    print(f"FAIL: {e}")

try:
    import google.generativeai
    print("WARNING: Legacy SDK still present")
except ImportError:
    print("SUCCESS: Legacy SDK removed")
