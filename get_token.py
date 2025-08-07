#!/usr/bin/env python3
"""
Get HuggingFace API Token
"""

print("🔑 HUGGINGFACE API TOKEN SETUP")
print("=" * 40)
print()
print("📝 To get your free HuggingFace API token:")
print("   1. Go to: https://huggingface.co/settings/tokens")
print("   2. Click 'New token'")
print("   3. Give it a name (e.g., 'NHAI_RAG')")
print("   4. Select 'Read' role")
print("   5. Copy the token")
print()
print("💡 Free tier allows 30,000 requests/month")
print()

token = input("Enter your HuggingFace API token: ").strip()

if token:
    with open("ragflow_integration/hf_token.txt", "w") as f:
        f.write(token)
    print("✅ Token saved successfully!")
    print("🚀 Now running RAGFlow setup...")
    
    # Run the setup
    import subprocess
    subprocess.run(["py", "ragflow_integration/setup_ragflow_no_docker.py"])
else:
    print("❌ No token provided. Setup cancelled.") 