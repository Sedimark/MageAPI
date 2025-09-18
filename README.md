# 🧙‍♂️ Mage AI API

![Docker Image](https://github.com/JarcauCristian/MageAPI/actions/workflows/docker_image.yml/badge.svg)

> **Automate Mage AI workflows through the power of code** ✨

Mage AI API provides a comprehensive REST API interface that automates most operations available in Mage AI, enabling seamless integration and programmatic control of your data pipelines.

---

## 🚀 Features

- **Pipeline Management** - Create, read, update, and delete pipelines
- **Block Operations** - Manage data blocks and transformations  
- **File Handling** - Upload, download, and manage project files
- **Real-time Monitoring** - WebSocket support for live pipeline status
- **Export Capabilities** - Export pipelines in multiple formats (including CWL)
- **RAG Integration** - AI-powered assistance for your workflows
- **Docker Ready** - Containerized deployment with official images

---

## 🏃‍♂️ Quick Start

### Using Docker (Recommended)

1. **Pull the official image:**
   ```bash
   docker pull ghcr.io/sedimark/mageapi/mage-api:latest
   ```

2. **Configure environment variables:**
   ```bash
   export BASE_URL="<your-mage-ai-url>"
   export EMAIL="<admin-email>"
   export PASSWORD="<admin-password>"
   export AUTH="true"  # or "false" for no auth
   export OLLAMA_URL="<ollama-instance-url>"
   export OLLAMA_MODEL="<model-name>"
   ```

3. **Run the container:**
   ```bash
   docker run -p 8000:8000 \
     -e BASE_URL=$BASE_URL \
     -e EMAIL=$EMAIL \
     -e PASSWORD=$PASSWORD \
     -e AUTH=$AUTH \
     -e OLLAMA_URL=$OLLAMA_URL \
     -e OLLAMA_MODEL=$OLLAMA_MODEL \
     ghcr.io/sedimark/mageapi/mage-api:latest
   ```

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `BASE_URL` | URL to your Mage AI deployment | ✅ |
| `EMAIL` | Admin account email | ✅ (if AUTH=true) |
| `PASSWORD` | Admin account password | ✅ (if AUTH=true) |
| `AUTH` | Enable authentication (`true`/`false`) | ✅ |
| `OLLAMA_URL` | OLLAMA instance URL | ❌ |
| `OLLAMA_MODEL` | Model name for OLLAMA | ❌ |

---

## 📚 API Documentation

Once the API is running, access the interactive documentation:

### 🔗 Documentation Links
- **Swagger UI**: [http://localhost:8000/mage/docs](http://localhost:8000/mage/docs)
- **Scalar UI**: [http://localhost:8000/mage/scalar](http://localhost:8000/mage/scalar)

The documentation provides:
- 📖 Complete endpoint reference
- 🧪 Interactive API testing
- 📋 Request/response examples
- 🔧 Schema definitions

---

## 🛠️ API Categories

Our API is organized into the following categories:

| Category | Description |
|----------|-------------|
| 🔄 **Pipeline Interactions** | Manage pipelines, templates, triggers, and execution |
| 🧱 **Block Interactions** | Handle data blocks and transformations |
| 📁 **File Interactions** | Upload, download, and manage project files |
| 📊 **Log Interactions** | Access and monitor pipeline logs |
| 🌐 **WebSocket Interactions** | Real-time pipeline status and updates |
| 🖥️ **Server Interactions** | Server management and health checks |
| 🤖 **RAG Interactions** | AI-powered assistance and recommendations |

---

## 🤝 Contributing

We welcome contributions! Please feel free to submit issues and pull requests.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

<div align="center">
  <strong>Happy coding! 🎉</strong>
</div>
