import os
import subprocess
import platform
import speech_recognition as sr
import pyttsx3
import threading
import time
import datetime
import webbrowser
import logging
import socket

HISTORY_FILE = "history.txt"

# Setup logging to history file
logging.basicConfig(filename=HISTORY_FILE, level=logging.INFO, format='[%(asctime)s] %(message)s')

# Initialize text-to-speech engine
engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

def log_request_response(request, response):
    logging.info(f"Request: {request}")
    logging.info(f"Response: {response}")

def open_app(app_name):
    system = platform.system()
    app_name_lower = app_name.lower()
    try:
        if system == "Windows":
            # Mapping of app names to commands or URLs
            app_commands = {
                "chrome": ["start", "chrome"],
                "brave": ["start", "brave"],
                "vscode": ["code"],
                "terminal": ["start", "cmd"],
                "youtube": "https://www.youtube.com",
                "whatsapp": ["start", "C:\\Users\\%USERNAME%\\AppData\\Local\\WhatsApp\\WhatsApp.exe"],
                "chat gpt": "https://chat.openai.com",
            }
            if app_name_lower in app_commands:
                cmd = app_commands[app_name_lower]
                if isinstance(cmd, list):
                    subprocess.Popen(cmd, shell=True)
                else:
                    # Open URL in default browser
                    webbrowser.open(cmd)
                return f"Opening {app_name}."
            else:
                # Try to open as website
                if app_name_lower.startswith("http") or "." in app_name_lower:
                    url = app_name_lower if app_name_lower.startswith("http") else "http://" + app_name_lower
                    webbrowser.open(url)
                    return f"Opening website {url}."
                else:
                    return f"App {app_name} not supported on Windows."
        else:
            return f"Unsupported OS: {system}"
    except Exception as e:
        return f"Failed to open {app_name}: {str(e)}"

def search_files(query, search_path="."):
    matches = []
    for root, dirs, files in os.walk(search_path):
        for file in files:
            try:
                with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                    content = f.read()
                    if query.lower() in content.lower():
                        matches.append(os.path.join(root, file))
            except:
                continue
    return matches

def control_volume(action):
    system = platform.system()
    try:
        if system == "Windows":
            import ctypes
            # Windows volume control requires additional libraries or complex code, skipping for now
            return "Volume control on Windows is not implemented yet."
        else:
            return f"Unsupported OS: {system}"
    except Exception as e:
        return f"Failed to control volume: {str(e)}"

def control_wifi(action):
    system = platform.system()
    try:
        if system == "Windows":
            if action == "on":
                subprocess.call(["netsh", "interface", "set", "interface", "Wi-Fi", "enabled"])
            elif action == "off":
                subprocess.call(["netsh", "interface", "set", "interface", "Wi-Fi", "disabled"])
            return f"WiFi turned {action}."
        else:
            return f"Unsupported OS: {system}"
    except Exception as e:
        return f"Failed to control WiFi: {str(e)}"


def listen_for_command():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        speak("Listening for your command.")
        audio = recognizer.listen(source, phrase_time_limit=5)
    try:
        command = recognizer.recognize_google(audio).lower()
        print(f"Command: {command}")
        return command
    except sr.UnknownValueError:
        speak("Sorry, I did not understand that.")
        return None
    except sr.RequestError:
        speak("Sorry, I am having trouble connecting to the speech service.")
        return None

import re

import re

def process_command(command):
    if not command:
        return "No command received."
    response = ""

    command = command.lower()

    # Open app or website
    open_match = re.search(r"open (.+)", command)
    if open_match:
        target = open_match.group(1).strip()
        # Use dynamic app list from open_app's app_commands keys
        apps = list({
            "chrome": None,
            "brave": None,
            "vscode": None,
            "terminal": None,
            "youtube": None,
            "whatsapp": None,
            "chat gpt": None,
        }.keys())
        if target in apps:
            response = open_app(target)
        else:
            # Check if target looks like a URL or website name
            if target.startswith("http") or "." in target:
                url = target if target.startswith("http") else "http://" + target
                webbrowser.open(url)
                response = f"Opening website {url}."
            else:
                response = f"Which app do you want to open? I don't recognize '{target}'."
        speak(response)
        return response

    # Search files
    search_match = re.search(r"search files? for (.+)", command)
    if search_match:
        query = search_match.group(1).strip()
        matches = search_files(query)
        if matches:
            response = f"Found {len(matches)} files containing '{query}': " + ", ".join(matches[:5])
        else:
            response = f"No files found containing '{query}'."
        speak(response)
        return response

    # Volume control
    if "volume" in command:
        if "up" in command:
            response = control_volume("up")
        elif "down" in command:
            response = control_volume("down")
        elif "mute" in command:
            response = control_volume("mute")
        else:
            response = "Specify volume action: up, down, or mute."
        speak(response)
        return response

    # WiFi control
    if "wifi" in command:
        if "on" in command:
            response = control_wifi("on")
        elif "off" in command:
            response = control_wifi("off")
        else:
            response = "Specify WiFi action: on or off."
        speak(response)
        return response

    # Time and date
    if "time" in command:
        now = datetime.datetime.now().strftime("%H:%M:%S")
        response = f"The current time is {now}."
        speak(response)
        return response

    if "date" in command:
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        response = f"Today's date is {today}."
        speak(response)
        return response

    # Open website
    website_match = re.search(r"open website (.+)", command)
    if website_match:
        url = website_match.group(1).strip()
        if url.startswith("http") or "." in url:
            url = url if url.startswith("http") else "http://" + url
            webbrowser.open(url)
            response = f"Opening website {url}."
        else:
            response = "Please specify a valid website URL."
        speak(response)
        return response

    response = "Sorry, I can't perform that command yet."
    speak(response)
    return response

def main():
    speak("Assistant is now running. Listening for commands.")
    while True:
        command = listen_for_command()
        response = process_command(command)
        print(f"Response: {response}")
        log_request_response(command, response)

if __name__ == "__main__":
    main()
