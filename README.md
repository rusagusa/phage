# Phage OS: Autonomous Multimodal Android Symbiote 🧬🦾

Phage OS (Code Name: **CLAW**) is an autonomous Android agent designed for the **Google Agent Challenge**. It inhabits your device using a high-fidelity multimodal loop, combining Gemini 2.5 Flash's reasoning with professional-grade Android automation.

## 🌟 Core Features
- **Project Isolation**: Every instruction creates a physical laboratory folder on the device for isolation.
- **Vision Protocol**: Pixel-perfect UI navigation using simultaneous XML map and Screenshot analysis.
- **Two-Way Terminal Sync**: The Brain "sees" everything—terminal output, notification lists, and logs are synced in real-time.
- **Decentralized Swarm**: Supports multiple users with unique Telegram bots and isolated phone nodes.
- **Self-Healing Loop**: Autonomous watchdog automatically kills hanging processes and retries tasks creatively.

## 🛠️ Technology Stack
- **Intelligence**: Google Gemini 2.5 Flash.
- **Backend**: Python (Functions Framework) on Google Cloud Run.
- **Database**: Firebase Firestore (for history, status, and multi-user configuration).
- **Client (Muscle)**: Bash + ADB + Termux on Android.
- **Dashboard**: React + Tailwind (Gemini-style laboratory interface).

## 🚀 Judge's Exhaustive Setup Guide
Follow these precise steps to deploy your own Phage instance.

### 1. The Muscle (Android Setup) - CRITICAL
Phage requires deep system access to perform its functions. Follow these steps on the Android device:

**A. Installation**
1.  Install [Termux](https://f-droid.org/en/packages/com.termux/ ) and the [Termux:API](https://f-droid.org/en/packages/com.termux.api/ ) app from F-Droid.
2.  Open Termux and run:
    ```bash
    pkg update && pkg upgrade -y
    pkg install termux-api jq curl adb -y
    termux-setup-storage
    ```

**B. Permissions (Manual Action Required)**
Go to Android Settings -> Apps -> **Termux:API** -> Permissions and **GRANT ALL**:
- [x] Camera
- [x] Contacts
- [x] Location (Always)
- [x] Microphone
- [x] Phone
- [x] SMS
- [x] Storage

**C. Initialization**
Run the launch command (Replace `YOUR_BRAIN_URL` with your Cloud Run deployment):
```bash
curl -s -L https://raw.githubusercontent.com/rusagusa/phage/main/phage.sh -o ~/phage.sh
chmod +x ~/phage.sh
# Start Phage! 
DEVICE_ID="node_judge" URL="https://YOUR_BRAIN_URL" ~/phage.sh
```

### 2. The Brain (Cloud Setup)
1.  **Clone this repo** and create a **Google Cloud Project**.
2.  Enable **Cloud Run**, **Artifact Registry**, and **Cloud Build**.
3.  Enable **Firestore** in Native Mode.
4.  Generate a service account key in Firebase Console and save it as `firebase_key.json` in the root.
5.  Deploy using the provided script (Injected with your API Keys):
    ```bash
    gcloud run deploy phage-gatway \
      --source . \
      --set-env-vars="TELEGRAM_TOKEN=YOUR_BOT_TOKEN,GEMINI_API_KEY=YOUR_API_KEY,DEVICE_ID=node_judge"
    ```

### 3. The Handshake (Telegram)
1.  Get a token from [@BotFather](https://t.me/botfather).
2.  Initialize the bot by sending `/start`.
3.  Phage will begin reporting heartbeats to the Firestore `status` collection.

## 📊 System Performance & Architecture

### Full Architecture Diagram
![System Architecture](architecture_diagram.png)

### System Evolution & Insights
![System Evolution](system_diagram_2.png)

### Cloud Real-time Execution Usage
![Cloud Usage](cloud_run_usage.png)

### Terminal Sync Logs (Full Duplex)
![Terminal Sync](terminal_logs.png)

### Code Structure (Autonomous Backbone)
![Code Structure](code_structure.png)

## 🎥 Proof of Deployment
- **API Reference**: Phage leverages the `google-genai` SDK for multimodal reasoning.
- **Video Demo**: [Watch the High-Order Agent in action](https://twitter.com/rusagusa/status/123456789)

---
*Created for the Google Agent Challenge. #GeminiLiveAgentChallenge*
