# NHAI Policy Circulars - RAGFlow Integration

This directory contains the integration of RAGFlow with the NHAI Policy Circulars monitoring system.

## Overview

RAGFlow is an open-source RAG (Retrieval-Augmented Generation) engine based on deep document understanding. This integration provides:

- **Advanced Document Processing**: Deep understanding of NHAI policy documents
- **Intelligent Search**: Semantic search across all policy circulars
- **Multi-Modal Support**: Handles text, tables, and scanned documents
- **Agentic Workflows**: Automated policy analysis and recommendations
- **Web Interface**: User-friendly dashboard for policy exploration

## Architecture

```
NHAI Policy Circulars System
├── Data Collection (nhai_scraper.py)
├── PDF Processing (pdf_text_extractor.py)
├── RAGFlow Integration
│   ├── Document Ingestion
│   ├── Vector Database
│   ├── Search Engine
│   └── Web Interface
└── Policy Analysis & Insights
```

## Setup Instructions

### 1. Prerequisites

- Docker and Docker Compose
- Python 3.10+
- At least 8GB RAM (16GB recommended)
- 20GB+ disk space

### 2. Install RAGFlow

```bash
# Clone RAGFlow
git clone https://github.com/infiniflow/ragflow.git
cd ragflow

# Start RAGFlow with Docker
cd docker
docker compose -f docker-compose.yml up -d
```

### 3. Configure for NHAI Data

1. **Update Configuration**: Modify `service_conf.yaml.template` for NHAI-specific settings
2. **Set API Keys**: Configure LLM providers (OpenAI, Anthropic, etc.)
3. **Customize Embeddings**: Set up domain-specific embedding models

### 4. Data Pipeline Integration

The integration pipeline:
1. **Scrape** NHAI circulars using existing `nhai_scraper.py`
2. **Extract** text using `pdf_text_extractor.py`
3. **Process** documents through RAGFlow's deep understanding
4. **Index** in vector database for semantic search
5. **Query** through RAGFlow's web interface

## Features

### Document Understanding
- **Policy Structure Analysis**: Automatically identifies policy sections, clauses, and requirements
- **Table Extraction**: Extracts structured data from policy tables
- **Cross-Reference Detection**: Links related policies and circulars
- **Compliance Mapping**: Maps policy requirements to implementation guidelines

### Search Capabilities
- **Semantic Search**: Find policies by meaning, not just keywords
- **Policy Comparison**: Compare different policy versions and amendments
- **Requirement Tracking**: Track policy requirements across multiple documents
- **Impact Analysis**: Analyze policy changes and their implications

### Agentic Features
- **Policy Summarization**: Automatic generation of policy summaries
- **Compliance Checking**: Verify implementation against policy requirements
- **Recommendation Engine**: Suggest relevant policies based on context
- **Change Detection**: Identify policy changes and their impact

## Usage

### Web Interface
1. Access RAGFlow at `http://localhost`
2. Upload NHAI policy documents
3. Use natural language queries to search policies
4. Generate insights and recommendations

### API Integration
```python
from ragflow_integration.nhai_rag_client import NHAIRAGClient

# Initialize client
client = NHAIRAGClient()

# Search policies
results = client.search_policies("land acquisition procedures")

# Get policy insights
insights = client.analyze_policy("7.1.88")
```

### Command Line
```bash
# Process all NHAI circulars
python ragflow_integration/process_circulars.py

# Search specific policy
python ragflow_integration/search_policy.py "1.1.14"

# Generate policy report
python ragflow_integration/generate_report.py
```

## Configuration

### Environment Variables
```bash
# RAGFlow Configuration
RAGFLOW_HOST=localhost
RAGFLOW_PORT=80
RAGFLOW_API_KEY=your_api_key

# LLM Configuration
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# Database Configuration
ELASTICSEARCH_URL=http://localhost:9200
MYSQL_HOST=localhost
MYSQL_PORT=3306
```

### Custom Settings
- **Document Processing**: Configure for NHAI-specific document formats
- **Embedding Models**: Use domain-specific models for better understanding
- **Search Parameters**: Optimize for policy-related queries
- **Output Formats**: Customize reports and insights format

## Monitoring and Maintenance

### Health Checks
```bash
# Check RAGFlow status
docker logs ragflow-server

# Monitor resource usage
docker stats

# Check database health
curl http://localhost:9200/_cluster/health
```

### Backup and Recovery
- **Regular Backups**: Backup vector database and document store
- **Version Control**: Track policy document versions
- **Disaster Recovery**: Automated recovery procedures

## Performance Optimization

### Resource Allocation
- **CPU**: Allocate 4+ cores for processing
- **Memory**: 16GB+ RAM for large document sets
- **Storage**: SSD recommended for fast I/O
- **GPU**: Optional for accelerated processing

### Scaling
- **Horizontal Scaling**: Add more RAGFlow instances
- **Load Balancing**: Distribute queries across instances
- **Caching**: Implement Redis caching for frequent queries

## Security Considerations

### Access Control
- **Authentication**: Implement user authentication
- **Authorization**: Role-based access control
- **Audit Logging**: Track all policy access and modifications

### Data Protection
- **Encryption**: Encrypt sensitive policy data
- **Compliance**: Ensure GDPR and data protection compliance
- **Backup Security**: Secure backup storage and access

## Troubleshooting

### Common Issues
1. **Memory Issues**: Increase Docker memory allocation
2. **Processing Errors**: Check document format compatibility
3. **Search Problems**: Verify embedding model configuration
4. **Performance Issues**: Optimize resource allocation

### Support
- **Documentation**: Refer to RAGFlow documentation
- **Community**: Join RAGFlow Discord and GitHub discussions
- **Logs**: Check detailed logs for error diagnosis

## Future Enhancements

### Planned Features
- **Real-time Updates**: Live policy change notifications
- **Advanced Analytics**: Policy impact and compliance analytics
- **Integration APIs**: Connect with other government systems
- **Mobile Interface**: Mobile app for policy access

### Research Areas
- **Policy Evolution**: Track policy changes over time
- **Compliance Automation**: Automated compliance checking
- **Predictive Analytics**: Predict policy impacts and requirements
- **Natural Language Generation**: Generate policy summaries and reports 