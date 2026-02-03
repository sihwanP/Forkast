import sys
import os

try:
    import google
    print(f"GOOGLE PATH: {google.__path__}")
except ImportError:
    print("GOOGLE not found")

try:
    import google.genai
    print(f"GENAI FILE: {google.genai.__file__}")
except ImportError as e:
    print(f"GENAI IMPORT ERROR: {e}")

print(f"SYS.PATH: {sys.path}")
