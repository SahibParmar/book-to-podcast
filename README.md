## 📚 Book-to-Podcast Generator

Transform any book or long-form content in **PDF format** into an engaging, human-like **conversational podcast** — complete with natural-sounding audio and a full transcript.

---

### ✨ Features

* 🔀 Converts any **PDF book/article** into a podcast
* 🎧 Creates a **duo-host style conversation** between male and female voices
* 🧠 Uses **Google Gemini 2.0 (Flash)** to understand and summarize content
* 🔊 Outputs **realistic TTS audio** using `edge-tts` (Microsoft's voice model)
* 📄 Generates and shows a **full podcast transcript**
* 📀 Allows users to **download both the MP3 and transcript**

> Note: ⚠️ This project uses publicly available neural voices via `edge-tts`.

---

### 🚀 Demo

> Upload a book PDF and click "Generate" to get your personalized podcast!
![image](https://github.com/user-attachments/assets/9e3703c8-9a08-4e3e-a685-9ec576267714)
![image](https://github.com/user-attachments/assets/b978a522-cb54-4038-b6a1-b42a05195280)

---

### 🔧 Installation

> Requires: Python 3.10+, FFmpeg, Chrome/Edge, and internet for Gemini API.

#### 1. Clone the repository

```bash
git clone https://github.com/SahibParmar/book-to-podcast.git
cd book-to-podcast
```

#### 2. Install dependencies

```bash
pip install -r requirements.txt
```

#### 3. Setup `.env` for Google Gemini

Create a `.env` file in the root folder with the following:

```
GOOGLE_API_KEY=your_google_gemini_api_key_here
```

#### 4. Additional Setup Requirements

Before running the app, make sure:

* You have **FFmpeg** installed and added to your system PATH.
* Your browser (Edge/Chrome) is installed.
* You are connected to the internet for Gemini to work.

#### 5. Launch the app

```bash
python App.py
```

---

### ✅ How It Works

1. 📄 **Upload a PDF** — any book or article.
2. 🤖 AI reads, splits, embeds, and queries your document.
3. 🧠 Gemini generates summaries and conversational questions.
4. 🗣️ Two AI-generated hosts (male & female) **talk about your book**.
5. 🎧 Final audio is saved as `podcast.mp3`, with transcript as `script.txt`.

---

### 📂 Output Files

* `podcast.mp3` – The final audio output.
* `script.txt` – The AI-generated transcript.

---

### 🧪 Tech Stack

| Layer          | Tool/Library                                           |
| -------------- | ------------------------------------------------------ |
| UI             | [Gradio](https://gradio.app)                           |
| AI Model       | Google Gemini 2.0 Flash (via `langchain-google-genai`) |
| Embedding      | `all-MiniLM-L6-v2` via HuggingFace                     |
| Text-to-Speech | `edge-tts`                                             |
| Parsing PDFs   | `pypdf`                                                |
| Vector DB      | `Chroma`                                               |

---

### 📌 Notes

* Use on **text-based PDFs** (not scanned images).
* Runs fully on **CPU** unless modified for GPU.
* Works best on **book-style PDFs** with continuous prose.
* Users must **set up all dependencies and environment** before running.

---

### 📜 License

This project is open-source and free to use under the MIT License.

---
