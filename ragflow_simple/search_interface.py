
import json
from pathlib import Path
from working_rag import initialize_rag, search_documents

def main():
    print("NHAI Policy Circulars Search")
    print("=" * 40)
    
    # Initialize RAG system
    rag = initialize_rag()
    
    # Load documents if not already loaded
    if not Path("./chroma_db").exists():
        print("Loading documents for first time...")
        from working_rag import load_and_index_documents
        load_and_index_documents()
    
    print("\nReady for queries! Type 'quit' to exit.")
    print("Example queries:")
    print("   - delegation of powers")
    print("   - policy circular")
    print("   - administration")
    print("   - finance")
    print()
    
    while True:
        query = input("Enter your search query: ").strip()
        
        if query.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
        
        if not query:
            continue
        
        print(f"\nSearching for: '{query}'")
        print("-" * 40)
        
        results = search_documents(query, top_k=5)
        
        if results and results['documents']:
            docs = results['documents'][0]
            metadatas = results['metadatas'][0]
            
            print(f"Found {len(docs)} results:\n")
            
            for i, (doc, metadata) in enumerate(zip(docs, metadatas)):
                print(f"{i+1}. {metadata.get('subject', 'No subject')}")
                print(f"   Date: {metadata.get('date', 'Unknown')}")
                print(f"   Category: {metadata.get('category', 'Unknown')}")
                print(f"   Content: {doc[:200]}...")
                print()
        else:
            print("No results found")
        
        print("-" * 40)

if __name__ == "__main__":
    main()
