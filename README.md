# MageAPI
This Project is an API written in Python with FastAPI, that acts as a wrapper over the API from Mage AI, to let someone interact and control the pipelines inside a Mage AI deployment.

# Running the API
The API can either be run standalone, or from kubernetes:

- To run with python:
    - First run from the base directory: ```pip install -r requirements.txt```
    - After then run: ```python main.py```
- To run from kubernetes: go to kubernetes directory and:
    - Use the mage-deployment.yaml file to run the pod with: ```kubectl add -f mage-deployment.yaml```
    - Use the mage-service.yaml file to run the: ```kubectl add -f mage-service.yaml```
    - Also add the mage-secret.yaml file: ```kubectl add -f mage-secret.yaml```
    - Lastly add ingress file for data routing: ```kubectl add -f mage-ingress.yaml``` 
