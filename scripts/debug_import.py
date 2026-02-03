try:
    from google import genai
    print("SUCCESS: from google import genai works")
    print(genai.__file__)
except ImportError as e:
    print(f"ERROR: {e}")

try:
    import google.genai
    print("SUCCESS: import google.genai works")
except ImportError as e:
    print(f"ERROR: {e}")
