# NHAI RAGFlow Integration Guide

## Quick Start

1. **Start RAGFlow Services:**
   ```bash
   ./start_nhai_ragflow.sh
   ```

2. **Access Web Interface:**
   - Open browser and go to: http://localhost
   - Login with: admin / nhai_admin_2025

3. **Process NHAI Circulars:**
   ```bash
   python ragflow_integration/process_circulars.py --max-circulars 10
   ```

4. **Search Policies:**
   ```bash
   python ragflow_integration/search_policy.py "land acquisition"
   ```

## Features

### Document Processing
- Automatic PDF text extraction with OCR
- Policy structure analysis
- Cross-reference detection
- Compliance mapping

### Search Capabilities
- Semantic search across all policies
- Policy comparison and version tracking
- Requirement analysis
- Impact assessment

### Analysis Tools
- Policy summarization
- Compliance checking
- Change detection
- Recommendation engine

## API Usage

```python
from ragflow_integration.nhai_rag_client import NHAIRAGClient

# Initialize client
client = NHAIRAGClient()

# Search policies
results = client.search_policies("land acquisition procedures")

# Analyze specific policy
analysis = client.analyze_policy("7.1.88")

# Get recommendations
recommendations = client.get_policy_recommendations("road construction")
```

## Configuration

### Environment Variables
- `RAGFLOW_HOST`: RAGFlow server host (default: localhost)
- `RAGFLOW_PORT`: RAGFlow server port (default: 80)
- `RAGFLOW_API_KEY`: API key for authentication

### Custom Settings
- Modify `ragflow/conf/nhai_service_conf.yaml` for NHAI-specific settings
- Update `ragflow/docker/.env` for Docker configuration

## Troubleshooting

### Common Issues
1. **Docker not running**: Start Docker Desktop
2. **Port conflicts**: Change port in docker-compose.yml
3. **Memory issues**: Increase Docker memory allocation
4. **Service startup failures**: Check logs with `docker-compose logs`

### Logs
- RAGFlow logs: `docker-compose -f ragflow/docker/docker-compose.yml logs -f`
- Processing logs: `ragflow_integration/logs/processing.log`

## Support

- RAGFlow Documentation: https://docs.ragflow.io
- GitHub Issues: https://github.com/infiniflow/ragflow/issues
- Community Discord: https://discord.gg/ragflow
