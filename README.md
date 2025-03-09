# 📚 Chat with Multiple PDFs using LangChain & FAISS

This is a **PDF-based chatbot application** that allows users to upload multiple PDFs and interact with them using **OpenAI** models. It leverages **LangChain** for conversational AI and **FAISS** for efficient vector storage.

---

## 🚀 Features

✅ **Upload multiple PDFs** and chat with their content\
✅ **Persistent FAISS Vector Store** for fast access\
✅ **User-friendly UI** built with **Streamlit**\
✅ **Text-to-Speech (TTS) Support** for bot responses\
✅ **Save & Download Chat History**\
✅ **Custom error handling** when no response is found

---

## 🔧 Installation & Setup

### **1️⃣ Clone this repository**

```sh
git clone https://github.com/YOUR_GITHUB_USERNAME/multiple-pdf-chat.git
cd multiple-pdf-chat
```

### **2️⃣ Create a virtual environment**

```sh
python -m venv venv
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate      # On Windows
```

### **3️⃣ Install dependencies**

```sh
pip install -r requirements.txt
```

### **4️⃣ Set up your OpenAI API Key**

Create a `.env` file and add your API key:

```
OPENAI_API_KEY=your_openai_api_key_here
```

---

## ▶️ **How to Run**

```sh
streamlit run app.py
```

Open the **local URL** provided by Streamlit to start using the chatbot.

---

## 📂 **Project Structure**

```
📂 multiple-pdf-chat
│── 📂 faiss_index/           # Stores FAISS vector database
│── 📂 utils.py               # Handles PDF processing & vector storage
│── 📂 html_lib.py            # Manages UI templates (bot/user chat, errors)
│── 📂 app.py                 # Main application logic
│── 📄 requirements.txt       # Dependencies
│── 📄 README.md              # Project documentation
│── 📄 .gitignore             # Files to exclude from Git
```

---

## 📌 **Key Technologies Used**

- [**Streamlit**](https://streamlit.io/) - Web UI
- [**LangChain**](https://www.langchain.com/) - Conversational AI framework
- [**FAISS**](https://faiss.ai/) - Vector database
- [**PyPDF2**](https://pypdf2.readthedocs.io/) - PDF processing
- [**gTTS**](https://gtts.readthedocs.io/) - Text-to-Speech
- [**dotenv**](https://pypi.org/project/python-dotenv/) - Environment variable management

---

## ⚡ **How FAISS Works in this Project**

- **First Run:** When you upload PDFs, **FAISS stores the vectors** in `faiss_index/`.
- **Subsequent Runs:** Instead of reprocessing PDFs, the chatbot **loads vectors from FAISS** for faster performance.

---


