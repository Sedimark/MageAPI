# Mage AI API
![Docker Image](https://github.com/JarcauCristian/MageAPI/actions/workflows/docker_image.yml/badge.svg)

Mage AI API tries to automate most of the things that can be done in Mage AI through the power of code.

The API is split in three main categories:
- Pipeline Interactions
- Block Interactions
- Kernel Interactions
- File Interactions

To run the API there are two possibilities:
- Locally:
  - Clone the repository
  - Install the requirements: `pip install -r requirements.txt`
  - Run: `python main.py`

- Docker:
  - Getting the official image with: `docker pull ghcr.io/sedimark/mageapi/mage-api:latest`
    ## Environment Variables
      - **BASE_URL** -> The URL to the Mage AI deployment
      - **EMAIL** -> The email of an account with admin role
      - **PASSWORD** -> The password of an account with admin role
      - **AUTH** -> Can have only two values **[true, false]** if it is false then EMAIL and PASSWORD shouldn't be provided
      - **OLLAMA_URL** -> The URL for an OLLAMA instance
      - **OLLAMA_MODEL** -> The model to use 
    - Run the image: `docker run -p 8000:8000 -e BASE_URL=<> -e EMAIL=<> -e PASSWORD=<> -e AUTH=<> -e OLLAMA_URL=<> -e OLLAMA_MODEL=<> ghcr.io/sedimark/mageapi/mage-api:development`
   
Accessing the API swagger documentation at http://localhost:8000/mage/docs or at http://localhost:8000/mage/scalar     
