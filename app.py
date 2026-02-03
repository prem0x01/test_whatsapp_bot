import requests
from flask import Flask, request

app = Flask(__name__)

# --- CONFIGURATION ---
ACCESS_TOKEN = "EAAUpMMwYUscBQu12Jy41DiUJgBlr8cWX3uan4bVZAlsLG0HaZBcg5N2QacVIcfiBeINo2wkYDqZBJfDZA0m8A5W6YFpiuwpROgAsLawMRbulPsNjSdqIlvHDyXT2ZCDcjaFXL7wuvzUHrwBd35sanaGy5xUxX6Qvhn5ZC4ZC0b77vofs1uZAblQyUTXLGNtKCk6hSp8wDTs8IPZBmDbpPhaswHqt2MUmqKeC2Vqtex0VOLCCS7xbNBJgZBHnZBkd8jH24L1aRllYXLZCFzzaMV7ysQUT2FXvjt9DGjRfxwZDZD"
PHONE_NUMBER_ID = "997884723406177"
VERIFY_TOKEN = "testSecretsOfT45T44P"

# Memory to store user progress (In production, use a Database like Redis or SQLite)
user_sessions = {}

def get_bot_response(sender_id, user_text):
    user_text = user_text.strip().lower()

    # If this is a new user or they say 'reset'
    if sender_id not in user_sessions or "reset" in user_text:
        user_sessions[sender_id] = {"step": 1, "answers": {}}
        return "Hi! Let's get started. 1/3: What is your name?"

    session = user_sessions[sender_id]
    step = session["step"]

    if step == 1:
        session["answers"]["name"] = user_text
        session["step"] = 2
        return f"Nice to meet you, {user_text.capitalize()}! 2/3: What is your favorite color?"

    elif step == 2:
        session["answers"]["color"] = user_text
        session["step"] = 3
        return "Got it! 3/3: What city do you live in?"

    elif step == 3:
        session["answers"]["city"] = user_text
        name = session["answers"]["name"].capitalize()
        color = session["answers"]["color"]
        city = session["answers"]["city"].capitalize()

        # Clear session after completion
        del user_sessions[sender_id]

        return (f"✅ All done! Here is what I learned:\n"
                f"👤 Name: {name}\n"
                f"🎨 Color: {color}\n"
                f"📍 City: {city}\n\n"
                f"Type 'Hi' to start again!")

@app.route("/webhook", methods=["GET"])
def verify():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Verification failed", 403

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    try:
        # Check if it's a message event
        entry = data['entry'][0]['changes'][0]['value']
        if 'messages' in entry:
            message = entry['messages'][0]
            sender_id = message['from']
            user_text = message['text']['body']

            # Generate and send response
            reply = get_bot_response(sender_id, user_text)
            send_whatsapp_message(sender_id, reply)
    except Exception as e:
        print(f"Error: {e}")

    return "OK", 200

def send_whatsapp_message(to, text):
    url = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }
    requests.post(url, json=payload, headers=headers)

if __name__ == "__main__":
    app.run(port=5000)
