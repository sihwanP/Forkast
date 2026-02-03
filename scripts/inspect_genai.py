import google.generativeai as genai
import inspect

print("GenerativeModel init args:", inspect.signature(genai.GenerativeModel.__init__))
print("configure args:", inspect.signature(genai.configure))
