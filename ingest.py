import os
from pydoc import doc
import re
import shutil
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from dotenv import load_dotenv

load_dotenv()
#print("API Key loaded:", os.getenv("OPENAI_API_KEY"))

if os.path.exists("vectorstore"):
    shutil.rmtree("vectorstore")

DATA_PATH = "data/"
VECTOR_PATH = "vectorstore/"


def load_documents():
    docs = []
    for file in os.listdir(DATA_PATH):
        if file.endswith(".pdf"):
            loader = PyPDFLoader(os.path.join(DATA_PATH, file))
            pdf_docs = loader.load()

            for doc in pdf_docs:
                doc.metadata["source"] = file

            docs.extend(pdf_docs)

    return docs


def split_by_sections(documents):
    section_docs = []

    #section_pattern = r"(?=\n?\d+\.\s)"  # matches "1. ", "2. "
    #section_pattern = r"(?=\n?\d+\.\s|(?=(\d+\))"  
    section_pattern = r"(?=\n?\d+\.\s)|(?=\(\d+\)\s)"
    

    for doc in documents:
        # ✅ ALWAYS keep full first page (important for definitions)
        if doc.metadata.get("page", 0) == 0:
            full_text = doc.page_content.strip()

            full_text = full_text.replace("\n", " ").replace("“", '"').replace("”", '"')

            section_docs.append(
                Document(
                    page_content=full_text,
                    metadata={**doc.metadata, "section": "intro"}
                )
            )
        #splits = re.split(section_pattern, doc.page_content)
        # fallback: if no section pattern, keep full page
        if not re.search(section_pattern, doc.page_content):
            splits = [doc.page_content]
        else:
            splits = re.split(section_pattern, doc.page_content)

        for chunk in splits:
            chunk = chunk.strip()

            #section_match = re.match(r"(\d+)\.", chunk)
            section_match = re.match(r"(\d+)\.|^\(?(\d+)\)", chunk)
            #section_num = section_match.group(1) if section_match else "unknown"
            if section_match:
                section_num = section_match.group(1) if section_match.group(1) else section_match.group(2)
            else:
                section_num = "unknown"

            # remove leading numbers like (7) or 7.
            chunk = re.sub(r"^\(?\d+\)?\.?\s*", "", chunk)
            #normalising quotes dashes,
            chunk = chunk.replace("\n", " ").replace("“", '"').replace("”", '"').replace("—", " ")
            
            chunk_lower = chunk.lower()

            # ❌ skip structural / useless chunks
            if "arrangement of sections" in chunk_lower:
                continue

            if "table of contents" in chunk_lower:
                continue

            if "chapter" in chunk_lower and len(chunk) < 120:
                continue

            if "section" in chunk_lower and len(chunk) < 80:
                continue
            # Keep meaningful chunks including definition
            if len(chunk) < 50:
                continue
            # boost useful chunks
            if "act" in chunk_lower and len(chunk) < 80:
                continue
            # Allow definitions even without periods
            #if "." not in chunk and "means" not in chunk.lower():
                #continue
            if len(chunk) < 40:
                continue
            
        

            metadata = doc.metadata.copy()
            metadata["section"] = section_num
            metadata["source"] = doc.metadata.get("source", "unknown")

            section_docs.append(
                Document(page_content=chunk, metadata=metadata)
            )

    return section_docs


def secondary_chunking(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=200
    )

    return splitter.split_documents(documents)


def create_vectorstore(documents):
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    db = FAISS.from_documents(documents, embeddings)

    db.save_local(VECTOR_PATH)


def main():
    print("Loading PDFs...")
    docs = load_documents()

    print("Splitting by sections...")
    section_docs = split_by_sections(docs)

    print(f"Section chunks: {len(section_docs)}")

    print("Applying secondary chunking...")
    final_docs = secondary_chunking(section_docs)

    print(f"Final chunks: {len(final_docs)}")

    '''# inspect some chunks
    for i in range(3):
        print(f"\nChunk {i+1} preview:")
        print(final_docs[i].page_content[:300])
        print(final_docs[i].metadata)'''

    # for testing
    #final_docs= final_docs[:50]
    #print(f"Using {len(final_docs)} chunks for embedding")

    #debugging chunks
    for doc in final_docs:
        if "real estate" in doc.page_content.lower():
            print("\nFOUND REAL ESTATE CHUNK:")
            print(doc.page_content[:300])
            print(doc.metadata)
            break

    print("Creating embeddings + FAISS index...")
    create_vectorstore(final_docs)

    print("Done. Vector store saved.")


if __name__ == "__main__":
    main()