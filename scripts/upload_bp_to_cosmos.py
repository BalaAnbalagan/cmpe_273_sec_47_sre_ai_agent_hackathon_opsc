#!/usr/bin/env python3
"""
Upload BP 10-K Embeddings to Cosmos DB for RAG queries
"""

import os
import sys
import json
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

load_dotenv()

MONGO_URL = os.getenv("COSMOS_MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = "sre_hackathon"
COLLECTION_NAME = "bp_documents"

async def upload_embeddings():
    """Upload BP embeddings to Cosmos DB"""

    print("\n" + "="*70)
    print("  BP 10-K Embeddings → Cosmos DB Upload")
    print("="*70 + "\n")

    # Load embeddings
    embeddings_files = [
        "demo-data/bp_2023_embeddings.json",
        "demo-data/bp_2024_embeddings.json"
    ]

    all_documents = []
    for file_path in embeddings_files:
        full_path = os.path.join(os.path.dirname(__file__), '..', file_path)
        print(f"📖 Loading {os.path.basename(file_path)}...")

        with open(full_path, 'r') as f:
            docs = json.load(f)
            all_documents.extend(docs)
            print(f"   ✅ Loaded {len(docs)} documents\n")

    print(f"📊 Total documents to upload: {len(all_documents)}\n")

    # Connect to MongoDB
    print(f"🔌 Connecting to MongoDB: {MONGO_URL}")
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    # Drop existing collection to start fresh
    print(f"🗑️  Dropping existing collection: {COLLECTION_NAME}")
    await collection.drop()
    print("   ✅ Collection dropped\n")

    # Upload documents in batches (reduced due to Cosmos DB RU limits)
    batch_size = 10  # Smaller batches for Cosmos DB
    total_uploaded = 0
    import time

    print(f"📤 Uploading documents in batches of {batch_size}...")
    for i in range(0, len(all_documents), batch_size):
        batch = all_documents[i:i + batch_size]

        # Prepare documents for MongoDB
        mongo_docs = []
        for doc in batch:
            mongo_doc = {
                "document_id": doc["document_id"],
                "year": doc["year"],
                "source": doc["source"],
                "text": doc["text"],
                "embedding": doc["embedding"],
                "word_count": doc["word_count"],
                "metadata": doc["metadata"]
            }
            mongo_docs.append(mongo_doc)

        # Insert batch with retry
        max_retries = 3
        for attempt in range(max_retries):
            try:
                result = await collection.insert_many(mongo_docs)
                total_uploaded += len(result.inserted_ids)
                print(f"   Batch {i//batch_size + 1}: Uploaded {len(result.inserted_ids)} documents " +
                      f"(Total: {total_uploaded}/{len(all_documents)})")
                break
            except Exception as e:
                if "429" in str(e) or "TooManyRequests" in str(e):
                    if attempt < max_retries - 1:
                        wait_time = 5 * (attempt + 1)
                        print(f"   ⏸️  Rate limited, waiting {wait_time}s...")
                        time.sleep(wait_time)
                    else:
                        print(f"   ❌ Failed after {max_retries} retries")
                        raise
                else:
                    raise

        # Add delay between batches to avoid throttling
        time.sleep(1)

    print(f"\n✅ Upload complete!\n")

    # Create index on document_id for faster lookups
    print("📇 Creating index on document_id...")
    await collection.create_index("document_id", unique=True)
    print("   ✅ Index created\n")

    # Verify upload
    count = await collection.count_documents({})
    print(f"📊 Verification:")
    print(f"   • Documents in collection: {count}")
    print(f"   • Expected: {len(all_documents)}")
    print(f"   • Match: {'✅ YES' if count == len(all_documents) else '❌ NO'}\n")

    # Sample query
    print("🔍 Sample query test:")
    sample = await collection.find_one({"year": "2024"})
    if sample:
        print(f"   ✅ Found document: {sample['document_id']}")
        print(f"      Year: {sample['year']}")
        print(f"      Source: {sample['source']}")
        print(f"      Text preview: {sample['text'][:100]}...")
        print(f"      Embedding dimensions: {len(sample['embedding'])}")
    else:
        print("   ❌ No documents found")

    print("\n" + "="*70)
    print("✅ BP Embeddings Successfully Uploaded to Cosmos DB!")
    print("="*70 + "\n")

    print("💡 Next Steps:")
    print("   1. Test RAG safety analysis endpoint")
    print("   2. Query: 'What are BP's hard hat requirements?'")
    print("   3. Use /sre/images/safety-analysis with BP RAG\n")

    client.close()

if __name__ == "__main__":
    asyncio.run(upload_embeddings())
