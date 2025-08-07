# 🚀 NHAI RAGFlow Demo - 2 Hour Setup Guide

## Quick Start (30 minutes)

### 1. **Prerequisites**
- ✅ Docker Desktop installed and running
- ✅ Windows 10/11
- ✅ Internet connection

### 2. **Setup Commands**
```bash
# Run the quick setup script
ragflow_integration/quick_demo_setup.bat
```

### 3. **Access the Demo**
- 🌐 **Web Interface**: http://localhost
- 🔑 **Login**: admin / nhai_admin_2025
- 🤖 **Ollama**: http://localhost:11434

## Demo Features

### 📄 **Document Processing**
- Upload NHAI PDFs via web interface
- Automatic OCR and text extraction
- Policy metadata extraction

### 🔍 **Search & Q&A**
- Semantic search across all policies
- Ask questions about NHAI policies
- Get policy summaries and analysis

### 📊 **Analysis Tools**
- Policy comparison
- Compliance checking
- Change detection

## Demo Scenarios

### Scenario 1: Policy Search
1. Upload 5-10 NHAI policy PDFs
2. Ask: "What are the land acquisition procedures?"
3. Show semantic search results

### Scenario 2: Policy Q&A
1. Ask: "What is the compensation structure for road projects?"
2. Show AI-generated answers with source documents

### Scenario 3: Policy Analysis
1. Upload multiple policy versions
2. Show change detection and comparison
3. Generate compliance reports

## Troubleshooting

### Common Issues
1. **Docker not running**: Start Docker Desktop
2. **Port conflicts**: Change ports in docker-compose.yml
3. **Model download slow**: Use smaller model like `llama3.1:8b`

### Quick Fixes
```bash
# Restart services
ragflow_integration/stop_demo.bat
ragflow_integration/quick_demo_setup.bat

# Check logs
docker-compose -f ragflow_integration/ragflow/docker/docker-compose.yml logs
```

## Alternative Models (If needed)

### Free Models Available
- **Ollama**: llama3.1:8b, llama3.1:70b, mistral:7b
- **HuggingFace**: Free API with token
- **OpenAI**: Free tier available

### Model Switching
Edit `ragflow_integration/demo_config.yaml`:
```yaml
user_default_llm:
  factory: 'Ollama'  # or 'HuggingFace', 'OpenAI'
  model_name: 'llama3.1:8b'  # or other model
```

## Performance Tips

### For Demo
- Use `llama3.1:8b` (faster, smaller)
- Limit to 50 documents for demo
- Enable caching for faster responses

### For Production
- Use larger models for better accuracy
- Scale with more resources
- Add authentication and security

## Stop Demo
```bash
ragflow_integration/stop_demo.bat
```

---

**🎯 Goal**: Show working RAG system with NHAI documents in under 2 hours! 