import os
import sqlite3
import shutil
from langchain_huggingface import HuggingFaceEmbeddings # Changed from OpenAI
from langchain_chroma import Chroma
from langchain_core.documents import Document

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), "data")
DB_PATH = os.path.join(DATA_DIR, "orders.db")
CHROMA_PATH = os.path.join(DATA_DIR, "chroma_db")

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

def init_sql_db():
    """Initialize a dummy SQL database for Order Status"""
    print(f"Creating SQL DB at {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS orders") 
    cursor.execute("CREATE TABLE orders (order_id TEXT, status TEXT, item TEXT)")
    
    data = [
        ("ORD-123", "Shipped", "Gaming Laptop"),
        ("ORD-456", "Processing", "Wireless Mouse"),
        ("ORD-789", "Delivered", "4K Monitor"),
        ("ORD-999", "Cancelled", "Mechanical Keyboard")
    ]
    cursor.executemany("INSERT INTO orders VALUES (?, ?, ?)", data)
    conn.commit()
    conn.close()
    print("✅ SQL Database initialized.")

def init_vector_db():
    """Initialize a Vector DB using Free Hugging Face Embeddings"""
    print(f"Creating Vector DB at {CHROMA_PATH}...")
    
    docs = [
        Document(page_content="Refunds are processed within 7 business days. No refunds on electronics after 30 days of purchase.", metadata={"topic": "refund"}),
        Document(page_content="Shipping is free for orders over $50. International shipping generally takes 14-21 days.", metadata={"topic": "shipping"}),
        Document(page_content="To return an item, generate a return label from the user dashboard. Returns are free.", metadata={"topic": "returns"}),
    ]
    
    # Clean up old DB if exists
    if os.path.exists(CHROMA_PATH):
        if os.path.isdir(CHROMA_PATH):
            shutil.rmtree(CHROMA_PATH)
        else:
            os.remove(CHROMA_PATH)
            
    print("⬇️  Downloading embedding model (this happens once)...")
    
    # USING HUGGING FACE (Local & Free)
    hf_embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    Chroma.from_documents(
        documents=docs, 
        embedding=hf_embeddings, 
        persist_directory=CHROMA_PATH
    )
    print("✅ Vector Database initialized.")

if __name__ == "__main__":
    init_sql_db()
    init_vector_db()
    print("\n🎉 Data setup complete!")