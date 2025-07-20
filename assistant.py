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

import webbrowser

def open_application(app_name):
    app_map = {
        "youtube": "https://www.youtube.com",
        "file explorer": "explorer",
        "whatsapp": r"C:\\Users\\{username}\\AppData\\Local\\WhatsApp\\WhatsApp.exe",
        "chrome": "start chrome",
        "notepad": "notepad",
        "calculator": "calc",
        "settings": "ms-settings:",
        "command prompt": "cmd",
        "powershell": "powershell",
        "windows": "explorer",
        # Add more mappings as needed
    }
    app_name_lower = app_name.lower()
    if app_name_lower in app_map:
        target = app_map[app_name_lower]
        if target.startswith("http"):
            webbrowser.open(target)
            return f"Opening {app_name} in your default browser."
        else:
            try:
                if app_name_lower == "whatsapp":
                    import getpass
                    username = getpass.getuser()
                    path = target.format(username=username)
                    subprocess.Popen(path)
                else:
                    subprocess.Popen(target, shell=True)
                return f"Opening {app_name}."
            except Exception as e:
                return f"Failed to open {app_name}: {str(e)}"
    else:
        return f"Application {app_name} not recognized."

import re
import pyautogui
import time

def listen_for_typing():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    speak("Please say the sentence you want me to type.")
    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio)
        speak(f"I heard: {text}. Typing now.")
        return text
    except Exception as e:
        speak("Sorry, I could not understand the sentence to type.")
        return ""

def press_keys(keys_str):
    keys = keys_str.lower().split()
    for key in keys:
        try:
            pyautogui.keyDown(key)
        except Exception:
            pass
    time.sleep(0.1)
    for key in reversed(keys):
        try:
            pyautogui.keyUp(key)
        except Exception:
            pass

def process_command(command):
    command = command.lower()
    # Handle press keys command
    press_pattern = re.compile(r"press (.+)")
    press_match = press_pattern.match(command)
    if press_match:
        keys_str = press_match.group(1)
        press_keys(keys_str)
        return f"Pressed keys: {keys_str}"

    # Handle type sentence command
    type_pattern = re.compile(r"type (.+)")
    type_match = type_pattern.match(command)
    if type_match:
        sentence = type_match.group(1)
        if sentence.strip() == "":
            sentence = listen_for_typing()
        pyautogui.write(sentence)
        return f"Typed sentence: {sentence}"

    # Existing open/send message pattern
    open_send_pattern = re.compile(r"open (\w+)(?: and send message to (\w+)(?: that (.+))?)?")
    match = open_send_pattern.match(command)
    if match:
        app = match.group(1)
        contact = match.group(2)
        message = match.group(3)
        if app == "whatsapp":
            if contact and message:
                # Placeholder for sending WhatsApp message functionality
                return f"Sending message to {contact} on WhatsApp: {message}"
            else:
                return open_application(app)
        else:
            return open_application(app)
    elif command.startswith("open "):
        app = command[5:].strip()
        # Check if app is a URL
        if app.startswith("http://") or app.startswith("https://"):
            webbrowser.open(app)
            return f"Opening {app} in your default browser."
        else:
            response = open_application(app)
            return response
    elif command.startswith("run "):
        cmd = command[4:].strip()
        response = execute_system_command(cmd)
        return response
    else:
        # Discussion feature removed; return default message
        return "Sorry, I can only perform system tasks right now."

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
            # Speak the response if it is a string
            if isinstance(response, str):
                speak(response)
            elif isinstance(response, dict):
                # If response is a dict, try to extract text and speak
                text_to_speak = ""
                if "parts" in response:
                    text_to_speak = " ".join([part.get("text", "") for part in response["parts"]]).strip()
                elif "content" in response:
                    text_to_speak = response.get("content", "")
                if text_to_speak:
                    speak(text_to_speak)
                else:
                    speak(str(response))
            else:
                speak(str(response))
            log_request_response(command, response if isinstance(response, str) else json.dumps(response))
        except sr.UnknownValueError:
            speak("Sorry, I did not understand that. Please try again.")
        except sr.RequestError as e:
            speak(f"Could not request results; {e}")
        except KeyboardInterrupt:
            speak("Goodbye!")
            break

if __name__ == "__main__":
    listen_and_respond()
