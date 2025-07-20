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
    try:
        if system == "Windows":
            if app_name.lower() == "chrome":
                subprocess.Popen(["start", "chrome"], shell=True)
            elif app_name.lower() == "brave":
                subprocess.Popen(["start", "brave"], shell=True)
            elif app_name.lower() == "vscode":
                subprocess.Popen(["code"], shell=True)
            elif app_name.lower() == "terminal":
                subprocess.Popen(["start", "cmd"], shell=True)
            else:
                return f"App {app_name} not supported on Windows."
        elif system == "Darwin":  # macOS
            if app_name.lower() == "chrome":
                subprocess.Popen(["open", "-a", "Google Chrome"])
            elif app_name.lower() == "brave":
                subprocess.Popen(["open", "-a", "Brave Browser"])
            elif app_name.lower() == "vscode":
                subprocess.Popen(["open", "-a", "Visual Studio Code"])
            elif app_name.lower() == "terminal":
                subprocess.Popen(["open", "-a", "Terminal"])
            else:
                return f"App {app_name} not supported on macOS."
        elif system == "Linux":
            if app_name.lower() == "chrome":
                subprocess.Popen(["google-chrome"])
            elif app_name.lower() == "brave":
                subprocess.Popen(["brave-browser"])
            elif app_name.lower() == "vscode":
                subprocess.Popen(["code"])
            elif app_name.lower() == "terminal":
                subprocess.Popen(["gnome-terminal"])
            else:
                return f"App {app_name} not supported on Linux."
        else:
            return f"Unsupported OS: {system}"
        return f"Opening {app_name}."
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
        elif system == "Darwin":
            if action == "up":
                subprocess.call(["osascript", "-e", "set volume output volume ((output volume of (get volume settings)) + 10) --100%"])
            elif action == "down":
                subprocess.call(["osascript", "-e", "set volume output volume ((output volume of (get volume settings)) - 10) --100%"])
            elif action == "mute":
                subprocess.call(["osascript", "-e", "set volume output muted true"])
            return f"Volume {action} executed."
        elif system == "Linux":
            if action == "up":
                subprocess.call(["amixer", "-D", "pulse", "sset", "Master", "10%+"])
            elif action == "down":
                subprocess.call(["amixer", "-D", "pulse", "sset", "Master", "10%-"])
            elif action == "mute":
                subprocess.call(["amixer", "-D", "pulse", "sset", "Master", "toggle"])
            return f"Volume {action} executed."
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
        elif system == "Darwin":
            if action == "on":
                subprocess.call(["networksetup", "-setairportpower", "en0", "on"])
            elif action == "off":
                subprocess.call(["networksetup", "-setairportpower", "en0", "off"])
            return f"WiFi turned {action}."
        elif system == "Linux":
            if action == "on":
                subprocess.call(["nmcli", "radio", "wifi", "on"])
            elif action == "off":
                subprocess.call(["nmcli", "radio", "wifi", "off"])
            return f"WiFi turned {action}."
        else:
            return f"Unsupported OS: {system}"
    except Exception as e:
        return f"Failed to control WiFi: {str(e)}"

# Removed listen_for_wake_word function as per user request

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

def process_command(command):
    if not command:
        return "No command received."
    response = ""
    if "open" in command:
        if "chrome" in command:
            response = open_app("chrome")
        elif "brave" in command:
            response = open_app("brave")
        elif "vscode" in command:
            response = open_app("vscode")
        elif "terminal" in command:
            response = open_app("terminal")
        else:
            # Try to open as website if command contains "open <something>"
            words = command.split()
            url = None
            for word in words:
                if word.startswith("http") or "." in word:
                    url = word
                    break
            if url:
                webbrowser.open(url)
                response = f"Opening website {url}."
            else:
                response = "Which app do you want to open?"
    elif "search file" in command or "search files" in command:
        query = command.replace("search files", "").replace("search file", "").strip()
        if query:
            matches = search_files(query)
            if matches:
                response = f"Found {len(matches)} files containing '{query}': " + ", ".join(matches[:5])
            else:
                response = f"No files found containing '{query}'."
        else:
            response = "Please specify what to search for."
    elif "volume" in command:
        if "up" in command:
            response = control_volume("up")
        elif "down" in command:
            response = control_volume("down")
        elif "mute" in command:
            response = control_volume("mute")
        else:
            response = "Specify volume action: up, down, or mute."
    elif "wifi" in command:
        if "on" in command:
            response = control_wifi("on")
        elif "off" in command:
            response = control_wifi("off")
        else:
            response = "Specify WiFi action: on or off."
    elif "time" in command:
        now = datetime.datetime.now().strftime("%H:%M:%S")
        response = f"The current time is {now}."
    elif "date" in command:
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        response = f"Today's date is {today}."
    elif "open website" in command:
        words = command.split()
        url = None
        for word in words:
            if word.startswith("http") or "." in word:
                url = word
                break
        if url:
            webbrowser.open(url)
            response = f"Opening website {url}."
        else:
            response = "Please specify a valid website URL."
    else:
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
