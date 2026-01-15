# 🎬 ReFlow Studio

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Release%20Candidate-orange)
![Platform](https://img.shields.io/badge/Platform-Windows-blue)

**ReFlow** is a local, privacy-focused AI video production pipeline. It automates the complex tasks of dubbing, censoring, and editing videos using state-of-the-art machine learning models, all wrapped in a premium "Glass/Dark" dashboard.

> **Note:** This tool processes all data locally on your GPU. No data is sent to the cloud.

---

## ✨ Key Features

### 🎙️ AI Dubbing (Auto-Translation)
- **Engine:** Uses **Coqui XTTS v2** for high-fidelity voice cloning and dubbing.
- **Workflow:** Transcribes original audio, translates text, and generates dubbed audio in the target language (Hindi, English, etc.) while preserving the original voice tone.
- **Documentary Mode:** Optional "Duck-and-Cover" mixing (keeps original background audio at 20% volume).

### 🔇 Smart Censorship
- **Audio:** Uses **OpenAI Whisper** to transcribe text and `better_profanity` to identify offensive keywords. Automatically mutes or "bleeps" specific timestamps.
- **Visual:** Integrates **NudeNet** to detect NSFW visual content frame-by-frame and applies a Gaussian blur to specific regions automatically.

### 🖥️ Modern Dashboard UI
- Built with **CustomTkinter** for a high-DPI, responsive interface.
- **Queue System:** Batch process multiple videos in one go.
- **Live Stats:** Real-time tracking of processing speed, total jobs, and system status.
- **Dual Theme:** One-click toggle between "Deep Night" (Cyberpunk) and "Clean Light" modes.

---

## 🛠️ Tech Stack

* **GUI:** Python CustomTkinter (Modern UI)
* **Audio AI:** OpenAI Whisper (Transcription), Coqui XTTS v2 (Dubbing)
* **Vision AI:** NudeNet (Object Detection)
* **Processing:** FFmpeg (Media merging and encoding)
* **Backend:** PyTorch (Tensor computation)

---

## 🚀 Installation

### Prerequisites
* Windows 10/11 (NVIDIA GPU recommended for speed)
* Python 3.10+
* [FFmpeg](https://ffmpeg.org/download.html) installed and added to System PATH.

### Setup
1.  **Clone the repository**
    ```bash
    git clone [https://github.com/ananta-sj/ReFlow.git](https://github.com/ananta-sj/ReFlow.git)
    cd ReFlow   
    ```

2.  **Install Dependencies**
    *(Note: Some AI models require specific PyTorch versions)*
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the App**
    ```bash
    python main.py
    ```

---

## ⚠️ Legal & Ethical Disclaimer

**ReFlow Studio is a technical demonstration of local AI capabilities.**

* **Model Licenses:** This project uses Coqui XTTS (CPML) and NudeNet. Ensure you comply with their specific licenses if you intend to use this software for commercial purposes.
* **Content Usage:** The developer is not responsible for any misuse of this software to alter content without consent. Please use responsibly.

---
## 📸 Screenshots

| Dark Mode | Light Mode |
|:---:|:---:|
| ![Dark](screenshot_dark.png) | ![Light](screenshot_light.png) |

## 🔧 Troubleshooting

**1. "FFmpeg not found" Error:**
* Make sure you downloaded FFmpeg and added the `bin` folder to your Windows System PATH.
* Restart your computer after installing FFmpeg.

**2. App crashes on startup:**
* Check if you have the latest Visual C++ Redistributables installed.
* Ensure your NVIDIA drivers are up to date (if using GPU).

**3. "Visual Blur" is slow:**
* NudeNet requires downloading models on the first run. Please be patient; it will be faster next time.
---
## 🤝 Contributing

Contributions are welcome!
1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.