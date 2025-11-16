#!/usr/bin/env python3
"""
Process BP Annual Reports (10-K) PDFs for RAG Integration
Extracts text, creates embeddings, and stores in Cosmos DB for Cohere RAG
"""

import os
import sys
import PyPDF2
import cohere
from typing import List, Dict
import json
from datetime import datetime
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

load_dotenv()

COHERE_API_KEY = os.getenv("COHERE_API_KEY")
PDF_DIR = os.path.join(os.path.dirname(__file__), '..', '.source_doc', 'BP_10K')

def extract_pdf_text(pdf_path: str) -> str:
    """Extract text from PDF"""
    print(f"📄 Extracting text from {os.path.basename(pdf_path)}...")

    text = ""
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        total_pages = len(pdf_reader.pages)

        for page_num in range(total_pages):
            if page_num % 10 == 0:
                print(f"   Processing page {page_num}/{total_pages}...")
            page = pdf_reader.pages[page_num]
            text += page.extract_text() + "\n\n"

    print(f"✅ Extracted {len(text):,} characters from {total_pages} pages\n")
    return text

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[Dict]:
    """Split text into overlapping chunks for better context"""
    chunks = []
    words = text.split()

    for i in range(0, len(words), chunk_size - overlap):
        chunk_words = words[i:i + chunk_size]
        chunk_text = ' '.join(chunk_words)

        if len(chunk_text) > 100:  # Skip very small chunks
            chunks.append({
                "text": chunk_text,
                "chunk_id": len(chunks),
                "word_count": len(chunk_words)
            })

    return chunks

def create_embeddings(chunks: List[Dict], year: str) -> List[Dict]:
    """Create Cohere embeddings for text chunks"""
    print(f"🧠 Creating embeddings for {len(chunks)} chunks from BP {year} report...")

    co = cohere.Client(COHERE_API_KEY)

    # Process in batches
    batch_size = 96  # Cohere API limit
    embedded_chunks = []

    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        texts = [chunk["text"] for chunk in batch]

        print(f"   Processing batch {i//batch_size + 1}/{(len(chunks)-1)//batch_size + 1}...")

        response = co.embed(
            texts=texts,
            model="embed-english-v3.0",
            input_type="search_document"
        )

        for j, embedding in enumerate(response.embeddings):
            embedded_chunks.append({
                "document_id": f"bp-{year}-chunk-{chunks[i+j]['chunk_id']}",
                "year": year,
                "source": f"BP Annual Report {year}",
                "text": chunks[i+j]["text"],
                "embedding": embedding,
                "word_count": chunks[i+j]["word_count"],
                "metadata": {
                    "document_type": "annual_report",
                    "company": "BP",
                    "year": year,
                    "chunk_id": chunks[i+j]["chunk_id"]
                }
            })

    print(f"✅ Created {len(embedded_chunks)} embeddings\n")
    return embedded_chunks

def save_to_json(data: List[Dict], filename: str):
    """Save processed data to JSON file"""
    output_path = os.path.join(os.path.dirname(__file__), '..', 'demo-data', filename)

    # Create demo-data directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    print(f"💾 Saving data to {filename}...")
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"✅ Saved {len(data)} documents to {output_path}\n")

def create_rag_index(embedded_chunks: List[Dict]):
    """Create searchable index for RAG queries"""
    print("📊 Creating RAG search index...")

    index = {
        "created_at": datetime.utcnow().isoformat() + "Z",
        "total_documents": len(embedded_chunks),
        "documents": embedded_chunks,
        "search_examples": [
            "How many safety incidents occurred in BP operations in 2024?",
            "Describe BP Oil Drill Operations and Hard Hat requirements",
            "What were BP's safety compliance measures in 2023?",
            "BP renewable energy investments",
            "BP carbon reduction targets"
        ]
    }

    return index

def main():
    print("\n" + "="*70)
    print("  BP Annual Reports - RAG Processing Pipeline")
    print("  Processing 10-K PDFs for Cohere Integration")
    print("="*70 + "\n")

    if not COHERE_API_KEY or COHERE_API_KEY == "your-cohere-api-key-here":
        print("❌ Error: COHERE_API_KEY not set in environment")
        print("   Set it in .env file or export COHERE_API_KEY=your-key")
        return

    # Process each PDF
    all_embedded_docs = []

    for year in ["2023", "2024"]:
        pdf_file = f"bp-annual-report-and-form-20f-{year}.pdf"
        pdf_path = os.path.join(PDF_DIR, pdf_file)

        if not os.path.exists(pdf_path):
            print(f"⚠️  Warning: {pdf_file} not found, skipping...\n")
            continue

        print(f"📋 Processing BP {year} Annual Report")
        print("-" * 70 + "\n")

        # Extract text
        text = extract_pdf_text(pdf_path)

        # Save raw text
        text_file = f"bp_{year}_raw_text.txt"
        text_path = os.path.join(os.path.dirname(__file__), '..', 'demo-data', text_file)
        os.makedirs(os.path.dirname(text_path), exist_ok=True)
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"💾 Saved raw text to {text_file}\n")

        # Chunk text
        print(f"✂️  Chunking text...")
        chunks = chunk_text(text, chunk_size=800, overlap=150)
        print(f"✅ Created {len(chunks)} text chunks\n")

        # Create embeddings
        embedded_chunks = create_embeddings(chunks, year)
        all_embedded_docs.extend(embedded_chunks)

        # Save year-specific data
        save_to_json(embedded_chunks, f"bp_{year}_embeddings.json")

    # Create combined RAG index
    if all_embedded_docs:
        print("\n" + "="*70)
        rag_index = create_rag_index(all_embedded_docs)
        save_to_json([rag_index], "bp_rag_index.json")

        print(f"""
✅ RAG Processing Complete!

📊 Summary:
   • Total documents processed: {len(all_embedded_docs)}
   • Years covered: 2023, 2024
   • Embedding model: embed-english-v3.0
   • Ready for Cohere RAG queries

🔍 Sample RAG Queries:
   1. "How many safety incidents occurred in BP operations in 2024?"
   2. "Describe BP Oil Drill Operations and Hard Hat requirements"
   3. "What were BP's carbon reduction targets?"

📁 Output Files:
   • demo-data/bp_2023_embeddings.json
   • demo-data/bp_2024_embeddings.json
   • demo-data/bp_rag_index.json
   • demo-data/bp_2023_raw_text.txt
   • demo-data/bp_2024_raw_text.txt

💡 Next Steps:
   1. Upload embeddings to Cosmos DB
   2. Test RAG queries via /sre/images/chat endpoint
   3. Integrate with safety compliance analysis
        """)
    else:
        print("\n❌ No PDFs were processed successfully")

if __name__ == "__main__":
    main()
