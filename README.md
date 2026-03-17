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

## 🚀 Judge's Quick Start (Test Drive)
Judges can deploy their own instance of Phage in <5 minutes following these steps:

### 1. The Brain (Cloud Setup)
1.  **Clone this repo** and create a **Google Cloud Project**.
2.  Enable **Firestore** and the **Gemini API**.
3.  Generate a service account key in Firebase Console and save it as `firebase_key.json` in the root.
4.  Run `./deploy.sh` to push to Cloud Run. **Note your Service URL.**

### 2. The Muscle (Android Setup)
1.  Install **Termux** and the **Termux:API** app from F-Droid.
2.  Install dependencies in Termux: `pkg install termux-api jq curl adb`.
3.  Run the setup command (Replace `YOUR_BRAIN_URL` with your Cloud Run URL):
    ```bash
    curl -s -L https://raw.githubusercontent.com/rusagusa/phage/main/phage.sh -o ~/phage.sh
    chmod +x ~/phage.sh
    # Start Phage!
    DEVICE_ID="node_judge" URL="https://YOUR_BRAIN_URL" ~/phage.sh
    ```

### 3. The Handshake (Telegram)
1.  Create a bot via [@BotFather](https://t.me/botfather) to get a **TOKEN**.
2.  Send `/token YOUR_TELEGRAM_TOKEN` to the Phage Dashboard or add it to the `users` collection in Firestore under your `chat_id`.
3.  Start chatting! Try: *"Phage, list my notifications and talk to me."*

## 📊 Architecture
![Architecture Diagram](https://raw.githubusercontent.com/rusagusa/phage/main/architecture_diagram.png)

## 🎥 Proof of Deployment & Demo
- **Live Demo Video**: [Watch the Phage Evolution here](https://twitter.com/rusagusa/status/123456789)
- **Deployment**: Phage leverages revisioned secret injection on Cloud Run for professional security.

---
*Created for the purposes of entering the Google Agent Challenge. #GeminiLiveAgentChallenge*
