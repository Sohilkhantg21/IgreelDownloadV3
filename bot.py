from flask import Flask, request
import requests
import json
import os

app = Flask(__name__)

BOT_TOKEN = "7544666074:AAFRGuGIt3S8-y-Ym3ZJWYd_0-H_rnNayVQ"
BOT_API = f"https://api.telegram.org/bot{BOT_TOKEN}"
ADMIN_ID = "6411315434"
CHANNEL_USERNAME = "@sohilscripter"

USERS_FILE = "users.json"

# Load existing users
if os.path.exists(USERS_FILE):
    with open(USERS_FILE, "r") as f:
        users = json.load(f)
else:
    users = []

def save_users():
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

def is_joined(user_id):
    url = f"{BOT_API}/getChatMember?chat_id={CHANNEL_USERNAME}&user_id={user_id}"
    res = requests.get(url).json()
    status = res.get("result", {}).get("status", "")
    return status in ["member", "administrator", "creator"]

def send_message(chat_id, text):
    requests.post(f"{BOT_API}/sendMessage", data={"chat_id": chat_id, "text": text})

def send_video(chat_id, url):
    requests.post(f"{BOT_API}/sendVideo", data={"chat_id": chat_id, "video": url})

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    message = data.get("message", {})
    text = message.get("text", "")
    chat_id = message.get("chat", {}).get("id")
    username = message.get("from", {}).get("username", "")

    # Register user
    if chat_id not in users:
        users.append(chat_id)
        save_users()
        send_message(ADMIN_ID, f"New user: @{username} ({chat_id})")

    # Force join check
    if not is_joined(chat_id):
        send_message(chat_id, f"⚠️ Join {CHANNEL_USERNAME} to use this bot!")
        return {"ok": True}

    # Handle message
    if "instagram.com/reel" in text:
        try:
            send_message(chat_id, "⬇️ Downloading Reel...")
            resp = requests.post("https://igram.world/api/ig", data={"link": text})
            result = resp.json()
            video_url = result['links'][0]['url']
            send_video(chat_id, video_url)
        except:
            send_message(chat_id, "Failed to download reel.")
    else:
        send_message(chat_id, "Send a valid Instagram Reel link.")
    return {"ok": True}
