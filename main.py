import functions_framework
import os
from google import genai
from google.cloud import firestore
from google.genai import types
import json
import requests
import re
from gtts import gTTS
import io
import time

# --- CONSTANTS (Configured via Cloud Run Environment Variables) ---
DEFAULT_TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "YOUR_TELEGRAM_TOKEN")
MODEL_ID = "gemini-2.5-flash" 
DEVICE_ID = os.getenv("DEVICE_ID", "kigali_node_01")

# --- LAZY INIT GLOBALS ---
db = None
ai_client = None

def get_db():
    global db
    if db is None:
        db = firestore.Client.from_service_account_json('firebase_key.json')
    return db

def get_client():
    global ai_client
    if ai_client is None:
        api_key = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY")
        ai_client = genai.Client(api_key=api_key)
    return ai_client

def log_to_db(msg_type, message):
    try:
        get_db().collection('logs').add({
            "type": msg_type,
            "message": message,
            "timestamp": firestore.SERVER_TIMESTAMP
        })
    except Exception as e:
        print(f"Log failed: {e}")

def get_user_token(chat_id):
    try:
        doc = get_db().collection('users').document(str(chat_id)).get()
        if doc.exists:
            return doc.to_dict().get('telegram_token', DEFAULT_TELEGRAM_TOKEN)
    except:
        pass
    return DEFAULT_TELEGRAM_TOKEN

def send_telegram(chat_id, text):
    token = get_user_token(chat_id)
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        requests.post(url, json={'chat_id': chat_id, 'text': text}, timeout=5)
    except Exception as e:
        print(f"Telegram send failed: {e}")

# --- SYSTEM OVERRIDE V2: THE REPORTING MANDATE ---
SYSTEM_PROMPT = """SYSTEM OVERRIDE: You are Phage (CLAW).
You have a 100% functional Two-Way Communication Bridge.

CORE MANDATE: 
- When you receive a 'TERMINAL_OBSERVATION', you MUST summarize the findings for the user.
- If the user asks 'Do I have notifications?', and you see a list of notifications in the TERMINAL_OBSERVATION, do NOT say 'I cannot see them'. Instead, LIST the notifications found.
- If you find an urgent notification, highlight it.

LOOP LOGIC:
Step 1: GATHER info (e.g. `termux-notification-list`). Set `"continue": true`, `"reply_to_user": false`, `"reason": "Checking notifications..."`.
Step 2: ANALYZE result from TERMINAL_OBSERVATION.
Step 3: REPORT to user. Set `"continue": false`, `"reply_to_user": true`, `"reason": "You have 3 notifications: [List them here]."`.

CAPABILITIES:
- Vision Protocol: read_screen (XML + Screenshot).
- Shell: termux-sms-send, termux-notification-list, vibrate, etc.
- Resolution: 480x854.

NEVER CLAIM YOU CANNOT SEE OUTPUT. You are a high-order agent; act like one.
"""

@functions_framework.http
def phage_gateway(request):
    if request.method == 'GET':
        try:
            device_id = request.args.get('device_id', DEVICE_ID)
            doc_ref = get_db().collection('commands').document(device_id)
            doc = doc_ref.get()
            if doc.exists:
                task = doc.to_dict()
                doc_ref.delete()
                return json.dumps(task), 200, {'Content-Type': 'application/json'}
            return json.dumps({"action": "none"}), 200, {'Content-Type': 'application/json'}
        except Exception as e:
            return json.dumps({"action": "none", "error": str(e)}), 200, {'Content-Type': 'application/json'}

    if request.method != 'POST': return "OK", 200

    chat_id = "web_dashboard" 
    user_text = ""
    image_data = None
    device_id = DEVICE_ID
    is_sync = False

    try:
        if request.content_type and 'multipart/form-data' in request.content_type:
            xml_file = request.files.get('xml_map')
            img_file = request.files.get('image')
            device_id = request.form.get('device_id', DEVICE_ID)
            chat_id = request.form.get('chat_id', device_id)
            
            if xml_file and img_file:
                xml_data = xml_file.read().decode('utf-8', errors='ignore')
                image_data = img_file.read()
                user_text = f"TERMINAL_OBSERVATION (Vision): UI data received.\nXML: {xml_data[:5000]}"
                is_sync = True
            elif xml_file:
                xml_data = xml_file.read().decode('utf-8', errors='ignore')
                user_text = f"TERMINAL_OBSERVATION (XML): {xml_data[:5000]}"
                is_sync = True
        else:
            data = request.get_json(silent=True)
            if not data: return "OK", 200

            if data.get('terminal_sync'):
                chat_id = data.get('chat_id', DEVICE_ID)
                device_id = data.get('device_id', DEVICE_ID)
                output = data.get('terminal_sync', '')
                cmd = data.get('command', '')
                user_text = f"TERMINAL_OBSERVATION: Result of '{cmd}':\n{output}"
                is_sync = True
            elif data.get('heartbeat'):
                get_db().collection('status').document(data.get('device_id', DEVICE_ID)).set({
                    "battery": data.get('battery'),
                    "last_seen": firestore.SERVER_TIMESTAMP
                }, merge=True)
                return "OK", 200
            elif 'message' in data:
                chat_id = data['message']['chat']['id']
                user_text = data['message'].get('text', '')

        if not user_text and not image_data: return "OK", 200

        # Memory Management
        history_ref = get_db().collection('conversations').document(str(chat_id))
        history_doc = history_ref.get()
        chat_history = history_doc.to_dict().get('messages', []) if history_doc.exists else []

        # Content Prep
        config = types.GenerateContentConfig(response_mime_type="application/json", temperature=0.1)
        contents = [types.Content(role="user", parts=[types.Part.from_text(text=SYSTEM_PROMPT)])]
        
        # System hint for syncs
        if is_sync:
            contents.append(types.Content(role="user", parts=[types.Part.from_text(text="[SYSTEM NOTICE: This IS the output of your previous command. Analyze it and report the content to the user now.]")]))

        for msg in chat_history[-35:]: # Max memory for complex logs
            contents.append(types.Content(role=msg["role"], parts=[types.Part.from_text(text=msg["text"])]))

        current_parts = [types.Part.from_text(text=f"New Input/Observation: {user_text[:4000]}")]
        if image_data:
            current_parts.append(types.Part.from_bytes(data=image_data, mime_type="image/jpeg"))
        contents.append(types.Content(role="user", parts=current_parts))

        # Call Gemini
        response = get_client().models.generate_content(model=MODEL_ID, contents=contents, config=config)
        raw_text = response.text.strip()
        parsed_data = json.loads(raw_text)
        parsed_data["chat_id"] = str(chat_id)

        # Save History
        chat_history.append({"role": "user", "text": user_text[:1500]})
        chat_history.append({"role": "model", "text": raw_text})
        history_ref.set({"messages": chat_history[-70:]})
        
        get_db().collection('commands').document(device_id).set(parsed_data)

        # Reply Logic
        should_reply = parsed_data.get('reply_to_user', not parsed_data.get('continue', False))
        
        if should_reply:
            reason_text = parsed_data.get('reason', '...')
            if str(chat_id) != "web_dashboard":
                send_telegram(chat_id, f"🧬 Phage: {reason_text}")

        return "OK", 200

    except Exception as e:
        log_to_db("error", f"Brain Error: {str(e)}")
        return "OK", 200