
# 📘 Legal RAG Assistant

## 🔍 Overview
This project is a **Retrieval-Augmented Generation (RAG) based Legal Assistant** that answers user queries strictly using provided legal documents.

It ensures:
- No hallucination
- Context-grounded answers
- Traceable sources

---

## 🎯 Objective
To build a domain-specific assistant that:
- Answers only from documents
- Supports follow-up questions
- Refuses when information is missing
- Demonstrates a complete RAG pipeline

---

## 🧠 Architecture

1. **Document Ingestion**
   - Load PDFs
   - Split into chunks
   - Generate embeddings
   - Store in FAISS vector DB

2. **Retrieval**
   - Convert Query -> Embedding	
   - Retrieve top-k relevant chunks

3. **Generation**
   - Inject context into LLM
   - Answer strictly from context

4. **UI Layer**
   - Streamlit interface
   - Displays answer + source
   - Captures feedback and store in file

## 🧠 Architecture Diagram

User Query
   ↓
Streamlit UI (app.py)
   ↓
Retriever (FAISS Vector Store)
   ↓
Top-K Relevant Chunks
   ↓
Prompt Builder (chatbot.py)
   ↓
LLM (OpenAI)
   ↓
Answer + Citations
   ↓
Feedback Logging

---
## 🧩 Design Decisions

- Used FAISS for efficient vector search
- Implemented strict prompting to avoid hallucination
- Added citation system for transparency
- Used Streamlit for quick UI development
- Feedback logging for future improvements

---

## 📂 Documents Used

- Consumer protection Act - https://www.indiacode.nic.in/bitstream/123456789/15256/1/eng201935.pdf

- Real Estate Act - https://www.indiacode.nic.in/bitstream/123456789/2158/3/A2016-16.pdf

- Transfer of Property Act - https://www.indiacode.nic.in/bitstream/123456789/2338/1/A1882-04.pdf


---

## ⚙️ Setup Instructions

### 1. Clone / Download project

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate   # Mac

3. Install dependencies

pip install -r requirements.txt

4. Add API Key

Create .env file:

OPENAI_API_KEY=your_key_here


⸻

▶️ Run the Project

Step 1: Ingest documents

python ingest.py

Step 2: Run chatbot UI

streamlit run app.py


⸻

💬 Sample Queries
	•	define consumer
	•	what is transfer of property
	•	what is real estate regulation and development act
	•	what is income tax (should refuse)

⸻

✅ Features
	•	RAG-based retrieval
	•	Context-aware conversation
	•	Strict hallucination control
	•	Source citations
	•	Streamlit UI
	•	Feedback mechanism

⸻

⚠️ Limitations
	•	Answers depend on document content
	•	Retrieval quality depends on chunking
	•	No external knowledge used

⸻

🧪 Example Behavior

Q: What is consumer?
A: Defined from Consumer Protection Act

Q: What is income tax?
A: I don’t have enough information in the provided documents.

Q: What is tranfer of property?
A: Retrieved from Transfer of Property Act.


⸻

📌 Tech Stack
	•	Python
	•	LangChain
	•	OpenAI API
	•	FAISS
	•	Streamlit

⸻

👤 Author
Sharmitha K


