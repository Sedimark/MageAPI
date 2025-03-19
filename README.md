# Mage AI API
![Docker Image](https://github.com/JarcauCristian/MageAPI/actions/workflows/docker_image.yml/badge.svg)

Mage AI API tries to automate most of the things that can be done in Mage AI through the power of code.

## API Categories
The API is split into four main categories:
- **Pipeline Interactions**
- **Block Interactions**
- **Kernel Interactions**
- **File Interactions**

## Running the API

### Locally
1. Clone the repository
2. Install the requirements:
   ```sh
   pip install -r requirements.txt
   ```
3. Run the application:
   ```sh
   python main.py
   ```

### Docker
1. Get the official image:
   ```sh
   docker pull ghcr.io/sedimark/mageapi/mage-api:latest
   ```

2. Set the environment variables:
   - **BASE_URL**: The URL to the Mage AI deployment
   - **EMAIL**: The email of an account with admin role
   - **PASSWORD**: The password of an account with admin role
   - **AUTH**: Can have only two values **[true, false]**; if it is false then EMAIL and PASSWORD shouldn't be provided
   - **OLLAMA_URL**: The URL for an OLLAMA instance
   - **OLLAMA_MODEL**: The model to use 

3. Run the image:
   ```sh
   docker run -p 8000:8000 -e BASE_URL=<> -e EMAIL=<> -e PASSWORD=<> -e AUTH=<> -e OLLAMA_URL=<> -e OLLAMA_MODEL=<> ghcr.io/sedimark/mageapi/mage-api:development
   ```

## Accessing the API Documentation
Access the API Swagger documentation at:
- [http://localhost:8000/mage/docs](http://localhost:8000/mage/docs)
- [http://localhost:8000/mage/scalar](http://localhost:8000/mage/scalar)

## API Endpoints

### Pipeline Interactions
- **GET /mage/pipeline/templates**: Retrieve pipeline templates.
- **GET /mage/pipeline/triggers**: Retrieve pipeline triggers.
- **GET /mage/pipeline/status/streaming**: Retrieve streaming pipeline status.
- **GET /mage/pipeline/status/batch**: Retrieve batch pipeline status.
- **GET /mage/pipelines**: Retrieve a list of pipelines.
- **GET /mage/pipelines/specific**: Retrieve specific pipelines.
- **GET /mage/pipeline/read**: Read a specific pipeline.
- **GET /mage/pipeline/read/full**: Read full details of a specific pipeline.
- **GET /mage/pipeline/read/predict/full**: Read full details of a prediction pipeline.
- **GET /mage/pipeline/history**: Retrieve pipeline history.
- **GET /mage/pipeline/description**: Retrieve pipeline description.
- **GET /mage/pipeline/block/templates**: Retrieve block templates.
- **GET /mage/pipeline/export/cwl**: Export pipeline to CWL.
- **GET /mage/pipeline/export**: Export pipeline.
- **PUT /mage/pipeline/rename**: Rename a pipeline.
- **PUT /mage/pipeline/trigger/status**: Change pipeline trigger status.
- **PUT /mage/pipeline/trigger/update**: Update pipeline trigger.
- **PUT /mage/pipeline/description**: Update pipeline description.
- **POST /mage/pipeline/create**: Create a new pipeline.
- **POST /mage/pipeline/create/template**: Create a pipeline from a template.
- **POST /mage/pipeline/create/tags**: Create tags for a pipeline.
- **POST /mage/pipeline/create/trigger**: Create a trigger for a pipeline.
- **POST /mage/pipeline/run**: Run a pipeline.
- **POST /mage/pipeline/variables**: Create variables for a pipeline.
- **POST /mage/pipeline/import**: Import a pipeline.
- **DELETE /mage/pipeline/trigger/delete/{trigger_id}**: Delete a pipeline trigger.
- **DELETE /mage/pipeline/delete**: Delete a pipeline.

### Block Interactions
- **GET /mage/block/model**: Retrieve block model.
- **GET /mage/block/read**: Read a specific block.
- **POST /mage/block/create**: Create a new block.
- **POST /mage/block/template/create**: Create a block template.
- **PUT /mage/block/update**: Update a block.
- **DELETE /mage/block/delete**: Delete a block.

### File Interactions
- **GET /mage/file/download**: Download a file.
- **GET /mage/file/download/plain**: Download a file in plain text.
- **GET /mage/file/figures**: Retrieve figures for a pipeline.
- **GET /mage/file/telemetry**: Retrieve telemetry data for a pipeline.
- **POST /mage/files/create**: Create a new file or folder.
- **DELETE /mage/files/delete**: Delete a file or folder.

### Log Interactions
- **GET /mage/log/pipeline/{pipeline_name}**: Retrieve logs for a pipeline.
- **GET /mage/log/pipeline/{pipeline_name}/{block_name}**: Retrieve logs for a specific block.

### WebSocket Interactions
- **/mage/validate**: Validate a pipeline.
- **/mage/block/generate**: Generate a block using RAG.

### Server Interactions
- **POST /mage/server/set**: Set server configuration.

### RAG Interactions
- **POST /mage/rag/add**: Add a document to RAG.
