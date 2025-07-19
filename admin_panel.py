import datetime
import re
from collections import Counter

HISTORY_FILE = "history.txt"

def parse_history():
    requests = []
    responses = []
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    entries = content.strip().split("\\n\\n")
    for entry in entries:
        lines = entry.split("\\n")
        req_line = next((l for l in lines if l.startswith("[") and "Request:" in l), None)
        res_line = next((l for l in lines if l.startswith("[") and "Response:" in l), None)
        if req_line and res_line:
            req_text = req_line.split("Request:")[1].strip()
            res_text = res_line.split("Response:")[1].strip()
            requests.append(req_text)
            responses.append(res_text)
    return requests, responses

def categorize_request(request):
    request = request.lower()
    if request.startswith("open "):
        return "System Command - Open"
    elif request.startswith("run "):
        return "System Command - Run"
    else:
        return "Conversation / Query"

def show_analytics():
    requests, responses = parse_history()
    total = len(requests)
    categories = [categorize_request(r) for r in requests]
    counts = Counter(categories)
    print(f"Total requests: {total}")
    print("Request categories:")
    for cat, count in counts.items():
        print(f"  {cat}: {count}")
    print("\nRecent requests and responses:")
    for i in range(max(0, total-10), total):
        print(f"{i+1}. Request: {requests[i]}")
        print(f"   Response: {responses[i]}")
        print("")

def main():
    print("Admin Panel - Personal Assistant")
    print("===============================")
    while True:
        print("\nOptions:")
        print("1. Show analytics")
        print("2. Show request-response history")
        print("3. Exit")
        choice = input("Enter your choice: ").strip()
        if choice == "1":
            show_analytics()
        elif choice == "2":
            requests, responses = parse_history()
            for i, (req, res) in enumerate(zip(requests, responses), 1):
                print(f"{i}. Request: {req}")
                print(f"   Response: {res}")
                print("")
        elif choice == "3":
            print("Exiting admin panel.")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
