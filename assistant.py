import os
import sys
import subprocess
import datetime
import json
import threading
from dotenv import load_dotenv
import speech_recognition as sr
import pyttsx3
import requests

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = os.getenv("GEMINI_API_URL")  # Add this to .env for correct endpoint URL

# Constants
HISTORY_FILE = "history.txt"

# Initialize text-to-speech engine
engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

def log_request_response(request_text, response_text):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] Request: {request_text}\n[{timestamp}] Response: {response_text}\n\n"
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry)

def call_gemini_api(prompt):
    if not GEMINI_API_KEY:
        return "Gemini API key not found in environment variables."
    # Use fixed Gemini API URL from the curl example
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    headers = {
        "X-goog-api-key": GEMINI_API_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            # The response structure may vary; adjust as needed
            # Try to extract generated text from response
            if "candidates" in result and len(result["candidates"]) > 0:
                content = result["candidates"][0].get("content", "")
                # Extract text from parts if available
                if isinstance(content, dict) and "parts" in content:
                    texts = [part.get("text", "") for part in content["parts"]]
                    return " ".join(texts).strip()
                elif isinstance(content, str):
                    return content.strip()
                else:
                    return "No response content found."
            return "No response content found."
        else:
            return f"Gemini API error: {response.status_code} {response.text}"
    except Exception as e:
        return f"Error calling Gemini API: {str(e)}"

def execute_system_command(command):
    try:
        # For safety, restrict commands or sanitize input in real use
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip() or "Command executed successfully with no output."
        else:
            return f"Error executing command: {result.stderr.strip()}"
    except Exception as e:
        return f"Exception during command execution: {str(e)}"

def process_command(command):
    command = command.lower()
    # Basic system commands examples
    if command.startswith("open "):
        app = command[5:].strip()
        # Try to open app using start on Windows
        response = execute_system_command(f'start "" "{app}"')
        return response
    elif command.startswith("run "):
        cmd = command[4:].strip()
        response = execute_system_command(cmd)
        return response
    else:
        # Use Gemini API for other queries/conversations
        response = call_gemini_api(command)
        return response

def listen_and_respond():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    speak("Hello, I am your personal assistant. How can I help you today?")
    while True:
        with mic as source:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)
        try:
            command = recognizer.recognize_google(audio)
            print(f"You said: {command}")
            response = process_command(command)
            print(f"Assistant: {response}")
            speak(response)
            log_request_response(command, response)
        except sr.UnknownValueError:
            speak("Sorry, I did not understand that. Please try again.")
        except sr.RequestError as e:
            speak(f"Could not request results; {e}")
        except KeyboardInterrupt:
            speak("Goodbye!")
            break

if __name__ == "__main__":
    listen_and_respond()
