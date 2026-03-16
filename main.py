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

# --- CONSTANTS ---
DEFAULT_TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "YOUR_TELEGRAM_TOKEN")
MODEL_ID = "gemini-2.5-flash" 
DEVICE_ID = os.getenv("DEVICE_ID", "kigali_node_01")

# --- LAZY INIT GLOBALS ---
db = None
ai_client = None

def get_db():
    global db
    if db is None:
        if os.path.exists('firebase_key.json'):
            db = firestore.Client.from_service_account_json('firebase_key.json')
        else:
            db = firestore.Client() # Fallback for Cloud Run environment
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
        # User requested "spot on" responses without "Phage:" drama
        requests.post(url, json={'chat_id': chat_id, 'text': text}, timeout=5)
    except Exception as e:
        print(f"Telegram send failed: {e}")

def send_telegram_voice(chat_id, text):
    token = get_user_token(chat_id)
    try:
        # Using tld='co.uk' for a slightly different pitch/accent (often sounds more professional/sharp)
        tts = gTTS(text=text, lang='en', tld='co.uk')
        voice_io = io.BytesIO()
        tts.write_to_fp(voice_io)
        voice_io.seek(0)
        
        url = f"https://api.telegram.org/bot{token}/sendVoice"
        files = {'voice': ('voice.ogg', voice_io, 'audio/ogg')}
        requests.post(url, data={'chat_id': chat_id}, files=files, timeout=12)
    except Exception as e:
        log_to_db("error", f"Voice conversion failed: {str(e)}")
        send_telegram(chat_id, text)

# --- SYSTEM OVERRIDE V6: PRECISION & ZERO-DRAMA ---
SYSTEM_PROMPT = """SYSTEM OVERRIDE: You are Phage, a precision-grade Autonomous Android Agent.
NO DRAMA. NO INTRODUCTIONS. NO "Phage reporting". BE SPOT ON.

CAPABILITY POOL (Use via "command" field):
- UI: read_screen, tap_text "Text", input tap X Y, input text 'msg'
- HARDWARE: termux-torch on/off, termux-vibrate, termux-volume music <0-15>, termux-brightness <0-255>
- SENSORS: termux-battery-status, termux-location, termux-camera-photo
- COMMS: termux-notification-list, termux-sms-list, termux-sms-send -n X -m Y, termux-telephony-call X
- TOOLS: Full Linux coreutils (ls, cat, grep, curl, etc.)

MANDATES & DIRECTIVES:
1. TWO-WAY SYNC (CRITICAL): If you need data (e.g. battery, location, notifications), YOU MUST set "continue": true and "reply_to_user": false. 
2. NO HALLUCINATION: Never say what you "will" do if you haven't seen the 'TERMINAL_OBSERVATION' yet. Only report facts once the data arrives.
3. CONCISE: Your "reason" must be the final report or immediate logic. Max 2 sentences.
4. VOICE: If "voice_reply" is true, your "reason" must be extremely short.

OUTPUT FORMAT (Strict JSON only):
{"action":"shell","command":"","reason":"","continue":true/false, "reply_to_user":true/false, "voice_reply":true/false}"""

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
    audio_data = None
    device_id = DEVICE_ID
    is_sync = False
    is_voice_input = False

    try:
        # ----- A. MULTIPART -----
        if request.content_type and 'multipart/form-data' in request.content_type:
            xml_file = request.files.get('xml_map')
            img_file = request.files.get('image')
            audio_file = request.files.get('audio')
            device_id = request.form.get('device_id', DEVICE_ID)
            chat_id = request.form.get('chat_id', device_id)
            
            if xml_file and img_file:
                xml_data = xml_file.read().decode('utf-8', errors='ignore')
                image_data = img_file.read()
                user_text = f"TERMINAL_OBSERVATION: read_screen UI data received.\nXML: {xml_data[:5000]}"
                is_sync = True
            elif xml_file:
                xml_data = xml_file.read().decode('utf-8', errors='ignore')
                user_text = f"TERMINAL_OBSERVATION: XML Map received:\n{xml_data[:5000]}"
                is_sync = True
            elif audio_file:
                audio_data = audio_file.read()
                user_text = f"AUDIO_OBSERVATION: Ambient audio sample received from device {device_id}."
        else:
            # ----- B. JSON -----
            data = request.get_json(silent=True)
            if not data: return "OK", 200

            if data.get('terminal_sync'):
                chat_id = data.get('chat_id', DEVICE_ID)
                device_id = data.get('device_id', DEVICE_ID)
                output = data.get('terminal_sync', '')
                cmd = data.get('command', '')
                user_text = f"TERMINAL_OBSERVATION: Result of '{cmd}':\n{output}"
                is_sync = True
                log_to_db("sync", f"Received terminal sync for {cmd}")
            elif data.get('heartbeat'):
                get_db().collection('status').document(data.get('device_id', DEVICE_ID)).set({
                    "battery": data.get('battery'),
                    "last_seen": firestore.SERVER_TIMESTAMP
                }, merge=True)
                return "OK", 200
            elif 'message' in data:
                chat_id = data['message']['chat']['id']
                if 'voice' in data['message']:
                    is_voice_input = True
                    file_id = data['message']['voice']['file_id']
                    token = get_user_token(chat_id)
                    file_resp = requests.get(f"https://api.telegram.org/bot{token}/getFile?file_id={file_id}").json()
                    file_path = file_resp['result']['file_path']
                    audio_data = requests.get(f"https://api.telegram.org/file/bot{token}/{file_path}").content
                    user_text = "VOICE_NOTE_INPUT"
                    log_to_db("input", "Voice note received from user")
                else:
                    user_text = data['message'].get('text', '')

        if not user_text and not image_data and not audio_data: return "OK", 200

        # ----- C. MEMORY -----
        history_ref = get_db().collection('conversations').document(str(chat_id))
        history_doc = history_ref.get()
        chat_history = history_doc.to_dict().get('messages', []) if history_doc.exists else []

        # ----- D. BUILD CONTENTS -----
        config = types.GenerateContentConfig(response_mime_type="application/json", temperature=0.1)
        contents = [types.Content(role="user", parts=[types.Part.from_text(text=SYSTEM_PROMPT)])]
        
        if is_sync:
            contents.append(types.Content(role="user", parts=[types.Part.from_text(text="[SYSTEM NOTICE: This is the real terminal feedback. Analyze it and report facts to the user now.]")]))

        for msg in chat_history[-20:]: 
            contents.append(types.Content(role=msg["role"], parts=[types.Part.from_text(text=msg["text"])]))

        current_parts = [types.Part.from_text(text=f"New Input: {user_text[:4000]}")]
        if image_data:
            current_parts.append(types.Part.from_bytes(data=image_data, mime_type="image/jpeg"))
        if audio_data:
            current_parts.append(types.Part.from_bytes(data=audio_data, mime_type="audio/mp3"))
        contents.append(types.Content(role="user", parts=current_parts))

        # ----- E. CALL AI -----
        response = get_client().models.generate_content(model=MODEL_ID, contents=contents, config=config)
        raw_text = response.text.strip()
        parsed_data = json.loads(raw_text)
        parsed_data["chat_id"] = str(chat_id)

        # ----- F. SAVE -----
        chat_history.append({"role": "user", "text": user_text[:1000]})
        chat_history.append({"role": "model", "text": raw_text})
        history_ref.set({"messages": chat_history[-40:]})
        
        get_db().collection('commands').document(device_id).set(parsed_data)

        # ----- G. REPLY LOGIC -----
        should_reply = parsed_data.get('reply_to_user', not parsed_data.get('continue', False))
        
        if should_reply:
            reason_text = parsed_data.get('reason', '...')
            if str(chat_id) != "web_dashboard":
                if parsed_data.get('voice_reply') or is_voice_input:
                    send_telegram_voice(chat_id, reason_text)
                else:
                    send_telegram(chat_id, reason_text)

        return "OK", 200

    except Exception as e:
        log_to_db("error", f"Brain Error: {str(e)}")
        return "OK", 200