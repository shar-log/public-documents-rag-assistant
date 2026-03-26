import os
from dotenv import load_dotenv

from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

# ✅ Load API key
load_dotenv(dotenv_path=".env")

# ✅ Initialize embeddings + vectorstore
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

db = FAISS.load_local(
    "vectorstore",
    embeddings,
    allow_dangerous_deserialization=True
)

# ✅ Initialize LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

chat_history = []


# ---------------- PROMPT ----------------
def build_prompt(context, question, history):
    history_text = ""
    for q, a in history[-3:]:
        history_text += f"User: {q}\nAssistant: {a}\n"

    return f"""
You are a legal assistant.

Use ONLY the provided context to answer the question.

The answer must be directly supported by the context.
Do NOT use your own knowledge.

If the answer is not explicitly present in the context, respond EXACTLY with:
"I don’t have enough information in the provided documents."

Do not infer definitions unless clearly stated in the context.

Context:
{context}

Conversation History:
{history_text}

Question:
{question}

Answer:
"""


# ---------------- RETRIEVAL ----------------
def retrieve_context(query):
    q = query.lower()
     
    if len(q.split()) <= 2:
        query = query +" act law regulation authority section clause"

    # plural normalization
    words = q.split()
    words = [w[:-1] if w.endswith("s") else w for w in words]
    query = " ".join(words)

    # light query enrichment
    if "define" in q:
        query += " meaning explanation"
    elif "what is" in q:
        query += " meaning explanation"
    else:
        query += " explanation"

    # retrieve
    docs = db.similarity_search(query, k=10)

    # simple rerank (DO NOT filter out score=0)
    STOPWORDS = {"define", "what", "is", "the", "a", "an", "meaning", "explanation", "by"}
    q_terms = [t for t in query.lower().split() if t not in STOPWORDS]

    top_semantic = docs[:5]

    scored = []
    for doc in top_semantic:
        text = doc.page_content.lower()
        score = sum(1 for t in q_terms if t in text)
        scored.append((score, doc))

    scored.sort(key=lambda x: x[0], reverse=True)

    # ✅ IMPORTANT: keep top 5 ALWAYS (no filtering)
    docs = [doc for score, doc in scored]

    # build context
    context = ""
    for doc in docs:
        context += f"Source: {doc.metadata.get('source')}\n"
        context += f"Section: {doc.metadata.get('section')}\n"
        context += doc.page_content + "\n\n---\n\n"

    return context, docs


# ---------------- CITATION ----------------
def build_citation(docs,user_input):
    seen = set()
    citations = []

    if not docs:
        return ""

    primary_source = docs[0].metadata.get("source", "unknown")

    # Step 1: section-based
    for doc in docs:
        source = doc.metadata.get("source", "unknown")
        section = doc.metadata.get("section", "unknown")

        if section != "unknown":
            key = (source, section)
            if key not in seen:
                seen.add(key)
                citations.append(f"{source}, Section {section}")

        if len(citations) >= 3:
            break

    # Step 2: same source fallback
    if len(citations) < 3:
        for doc in docs:
            source = doc.metadata.get("source", "unknown")
            if source == primary_source:
                if source not in seen:
                    seen.add(source)
                    citations.append(source)

            if len(citations) >= 3:
                break

    # Step 3: general fallback
    if len(citations) < 3:
        for doc in docs:
            source = doc.metadata.get("source", "unknown")
            if source not in seen:
                seen.add(source)
                citations.append(source)

            if len(citations) >= 3:
                break

    return "\nSources:\n- " + "\n- ".join(citations)


# ---------------- CHATBOT ----------------
def chatbot():
    print("📘 Legal RAG Assistant (type 'exit' to quit)\n")

    while True:
        user_input = input("You: ")

        if user_input.lower() == "exit":
            break

        context, docs = retrieve_context(user_input)

        prompt = build_prompt(context, user_input, chat_history)

        response = llm.invoke(prompt)
        answer = response.content.strip()

        # formatting
        answer = answer.replace("(i)", "\n(i)") \
                       .replace("(ii)", "\n(ii)") \
                       .replace("(iii)", "\n(iii)") \
                       .replace("(iv)", "\n(iv)")

        # refusal check
        if "enough information" in answer.lower():
            final_answer = answer
        else:
            citation = build_citation(docs)
            final_answer = answer + "\n" + citation

        print("\nAssistant:", final_answer, "\n")

        chat_history.append((user_input, answer))

def get_answer(user_input):
    context, docs = retrieve_context(user_input)
    prompt = build_prompt(context, user_input, chat_history)

    response = llm.invoke(prompt)
    answer = response.content.strip()

    # formatting
    answer = answer.replace("(i)", "\n(i)") \
                   .replace("(ii)", "\n(ii)") \
                   .replace("(iii)", "\n(iii)") \
                   .replace("(iv)", "\n(iv)")

    if "i don’t have enough information" in answer.lower():
        final_answer = answer
    else:
        citation = build_citation(docs, user_input)
        final_answer = answer + "\n" + citation

    chat_history.append((user_input, answer))

    return final_answer

if __name__ == "__main__":
    chatbot()
