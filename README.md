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

## 🚀 Spin-up Instructions

### 1. Cloud Setup
1.  Enable **Cloud Run** and **Firestore** in your Google Cloud Console.
2.  Create a Firebase service account key and save it as `firebase_key.json` in the root directory.
3.  Deploy the brain using the provided script:
    ```bash
    chmod +x deploy.sh
    ./deploy.sh
    ```

### 2. Muscle Preparation (Android)
1.  Install **Termux** and **ADB** on your Android device. 
2.  Enable Wireless ADB or connect via USB.
3.  Transfer `phage.sh` to your phone and run it:
    ```bash
    chmod +x phage.sh
    ./phage.sh
    ```

### 3. Dashboard Configuration
1.  Access the web dashboard.
2.  Navigate to **Protocol Setup**.
3.  Enter your `DEVICE_ID` and **Telegram Bot Token**.
4.  Send `/token YOUR_TOKEN` to your bot to finalize the handshake.

## 📊 Architecture
![Architecture Diagram](https://raw.githubusercontent.com/[YOUR_USER]/phage/main/architecture_diagram.png)

## 🎥 Proof of Deployment
- **Cloud Run Logs**: [Insert Image/Video Link here]
- **API Reference**: Phage leverages the `google-genai` SDK and utilizes `predict` and `generateContent` workflows for multimodal reasoning.

---
*Created for the purposes of entering the Google Agent Challenge. #GeminiLiveAgentChallenge*
