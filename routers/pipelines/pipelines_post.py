import os
import io
import re
import json
import httpx
import random
import string
import requests
from datetime import datetime
from dependencies import Token
from fastapi import APIRouter, HTTPException, UploadFile
from starlette.responses import JSONResponse
from utils.models import Pipeline, Secret, Trigger, Variables, Tag, Template, FederatedTemplate
from utils.name_generator import NameGenerator
from utils.replace_pipeline_name import replace_pipeline_name
from routers.blocks.blocks_get import get_template

router = APIRouter()

token = Token()


@router.post("/mage/pipeline/create", tags=["PIPELINES POST"])
async def pipeline_create(name: str, ptype: str):
    if token.check_token_expired():
        token.update_token()
    if token.token == "":
        raise HTTPException(status_code=500, detail="Could not get the token!")

    if ptype not in ["python", "streaming"]:
        raise HTTPException(status_code=400, detail="Only python and streaming are required for type")

    url = f'{os.getenv("BASE_URL")}/api/pipelines'

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token.token}',
        'X-API-KEY': os.getenv("API_KEY")
    }

    data = {
        "pipeline": {
            "name": name,
            "type": ptype,
            "description": "not created"
        }
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code != 200 or response.json().get("error") is not None:
        raise HTTPException(status_code=500, detail=response.json().get("error")["exception"])

    return JSONResponse(status_code=201, content="Pipeline Created")


@router.post("/mage/pipeline/create/template", tags=["PIPELINES POST"])
async def pipeline_create_template(template: Template):
    if token.check_token_expired():
        token.update_token()
    if token.token == "":
        raise HTTPException(status_code=500, detail="Could not get the token!")

    pattern = re.compile(r'^[a-z ]+$')

    if not pattern.fullmatch(template.pipeline_name):
        raise HTTPException(status_code=500, detail="Pipeline name can only contain lowercase letters and spaces!")

    url = f'{os.getenv("BASE_URL")}/api/pipelines?api_key={os.getenv("API_KEY")}'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token.token}',
    }

    data = {
        "api_key": os.getenv("API_KEY"),
        "pipeline": {
            "custom_template_uuid": template.template_uuid,
            "name": template.pipeline_name,
        }
    }

    response = requests.request("POST", url, headers=headers, json=data)

    print(response.json().get("error"))
    if response.status_code != 200 or response.json().get("error") is not None:
        raise HTTPException(status_code=500, detail=response.json().get("error")["exception"])

    return JSONResponse(status_code=201, content=f"Pipeline Created From Template {template.template_uuid.capitalize()}")


@router.post("/mage/pipeline/create/federated_learning", tags=["PIPELINES POST"])
async def pipeline_create_for_federated_learning(template: FederatedTemplate):
    """
     Tasks:
      1. Generate new pipeline of type
      2. Generate file for the FDML framework and add the url + store it
      3. Add blocks to the pipeline and create it accordingly ( the blocks from shamrock to shamrock and from fleviden for fleviden)

    """
    if token.check_token_expired():
        token.update_token()
    if token.token == "":
        raise HTTPException(status_code=500, detail="Could not get the token!")

    if template.framework not in ["fleviden","shamrock"]:
        raise HTTPException(status_code=400, detail="Framework should be of type fleviden or shamrock!")

    if len(template.url) == 0:
        raise HTTPException(status_code=400, detail="The URL must not be empty!")

    if len(template.token) == 0:
        raise HTTPException(status_code=400, detail="The token must not be empty!")
    
    if len(template.content) == 0:
        raise HTTPException(status_code=400, detail="The config file can not be empty!")
    
    
    new_pipeline_name = NameGenerator.generate(include_color=True)
    
    # create pipeline with random name
    
    url = f'{os.getenv("BASE_URL")}/api/pipelines'

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token.token}',
        'X-API-KEY': os.getenv("API_KEY")
    }

    data = {
        "pipeline": {
            "name": new_pipeline_name,
            "type": "streaming",
            "description": "not created"
        }
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code != 200 or response.json().get("error") is not None:
        raise HTTPException(status_code=500, detail=response.json().get("error")["exception"])

    # create config files for that pipeline
    url = f'{os.getenv("BASE_URL")}/api/folders?api_key={os.getenv("API_KEY")}'

    body = {
        "api_key": os.getenv("API_KEY"),
        "folder": {
            "name": new_pipeline_name,
            "overwrite": True,
            "path": "configs"
        }
    }

    response = requests.request("POST", url, json=body, headers=headers)

    if response.status_code != 200 or response.json().get("error") is not None:
        raise HTTPException(status_code=500, detail=f"Error creating the folder {new_pipeline_name}!")

    # aici e chestia cu pipeline-ul adica ce nume are va fii pus aici
    headers = {
            "Authorization": f"Bearer {token.token}",
            "accept": "application/json",
        }

    url = f"{os.getenv('BASE_URL')}/api/files?api_key={os.getenv('API_KEY')}"
    
    
    
    buffer = io.BytesIO(template.content.encode('utf-8'))

    overwrite = "true" 
    files = {
        "file": ("config.yaml", buffer, "text/yaml"),
        "json_root_body": (
            None,
            '{"api_key":"%s","dir_path":"%s","pipeline_zip":false,"overwrite":%s}' % (os.getenv('API_KEY'), f"configs/{new_pipeline_name}", overwrite),
        ), 
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, files=files)

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Error encountered when importing the file!")
    
    
    """
     The next steps here:
        1. Fetch the code for the blocks that are composing Fleviden
            - here you have to name them too and follow the payload structure
        2. Link the blocks and save them
        3. Save them to the endpoint
    
    """
    
    # 1. fetch the code for the 2 blocks
    # se preia content si variables
    # replace in cod acolo unde scrie <pipeline_name>
    # le creezi apoi le linkuiesti si la final salvezi
    
    
    importer_name = NameGenerator.generate(include_color=True)
    transformer_name = NameGenerator.generate(include_color=True)
    
    
    
    block_importer_data = {}
    block_transformer_data = {}
    
    if template.framework == "fleviden":
        block_importer_data = get_template("fleviden_initializer")
        block_transformer_data = get_template("fleviden_transformer")
    
    elif template.framework == "shamrock":
        block_importer_data = get_template("shamrock")
        block_transformer_data = get_template("shamrock_transformer")

    block_importer_data["content"] = replace_pipeline_name(block_importer_data["content"], new_pipeline_name)
    block_transformer_data["content"] = replace_pipeline_name(block_transformer_data["content"], new_pipeline_name)

    # here comes the logic that actually saves the block
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/plain, */*",
        "Authorization": f"Bearer {token.token}",
        "X-API-KEY": os.getenv("API_KEY")
    }
    
    

    # for the loader
    # config holds the variables
 
    
    try:
        config = json.loads(block_importer_data['variables'])
    except json.JSONDecodeError:
        print(f"Invalid JSON string: {block_importer_data['variables']}")
        # Handle the error appropriately
        config = {}  # or whatever default you want to use
    

    payload = {
        "block": {
            "name": importer_name,
            "language": "python",
            "type": "data_loader",
            "content": block_importer_data['content'],
            "configuration": config,
            "downstream_blocks": [transformer_name],
            "upstream_blocks": []
        }, 
        "api-key": os.getenv("API_KEY")
    }

    response = requests.request("POST", url=f'{os.getenv("BASE_URL")}/api/pipelines/{new_pipeline_name}/blocks?'
                                            f'api_key={os.getenv("API_KEY")}', headers=headers, json=payload)



    if response.status_code != 200 or response.json().get("error") is not None:
        raise HTTPException(status_code=500, detail=response.json().get("error")["exception"])
    

    
    try:
        config = json.loads(block_transformer_data['variables'])
    except json.JSONDecodeError:
        print(f"Invalid JSON string: {block_transformer_data['variables']}")
        # Handle the error appropriately
        config = {}  # or whatever default you want to use

    payload = {
        "block": {
            "name": transformer_name,
            "language": "python",
            "type": "transformer",
            "content": block_transformer_data['content'],
            "configuration": config,
            "downstream_blocks": [],
            "upstream_blocks": [importer_name]
        },
        "api-key": os.getenv("API_KEY")
    }

    response = requests.request("POST", url=f'{os.getenv("BASE_URL")}/api/pipelines/{new_pipeline_name}/blocks?'
                                            f'api_key={os.getenv("API_KEY")}', headers=headers, json=payload)



    if response.status_code != 200 or response.json().get("error") is not None:
        raise HTTPException(status_code=500, detail=response.json().get("error")["exception"])
    
    # here you need to tag the pipeline such that it can be seen on the UI
    
    url = f'{os.getenv("BASE_URL")}/api/pipelines/{new_pipeline_name}?update_content=true&api_key={os.getenv("API_KEY")}'

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token.token}',
        'X-API-KEY': os.getenv("API_KEY")
    }

    body = {
        "api_key": os.getenv("API_KEY"),
        "pipeline": {
            "tags": ["streaming"]
        }
    }

    response = requests.request("PUT", url, data=json.dumps(body), headers=headers)

    if response.status_code != 200 or response.json().get("error") is not None:
        raise HTTPException(status_code=500, detail=response.json().get("error")["exception"])
    
    
    return JSONResponse(status_code=201, content=f"Pipeline {new_pipeline_name} successfully created!")



@router.post("/mage/pipeline/create/tags", tags=["PIPELINES POST"])
async def pipeline_create_tag(tag: Tag):
    if token.check_token_expired():
        token.update_token()
    if token.token == "":
        raise HTTPException(status_code=500, detail="Could not get the token!")

    url = f'{os.getenv("BASE_URL")}/api/pipelines/{tag.name}?update_content=true&api_key={os.getenv("API_KEY")}'

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token.token}',
        'X-API-KEY': os.getenv("API_KEY")
    }

    body = {
        "api_key": os.getenv("API_KEY"),
        "pipeline": {
            "tags": tag.tags
        }
    }

    response = requests.request("PUT", url, data=json.dumps(body), headers=headers)

    if response.status_code != 200 or response.json().get("error") is not None:
        raise HTTPException(status_code=500, detail=response.json().get("error")["exception"])

    return JSONResponse(status_code=201, content="Tags created successfully!")


@router.post("/mage/pipeline/create/trigger", tags=["PIPELINES POST"])
async def pipeline_create_trigger(trigger: Trigger):
    if token.check_token_expired():
        token.update_token()
    if token.token == "":
        raise HTTPException(status_code=500, detail="Could not get the token!")

    if trigger.trigger_type not in ["time", "api"]:
        raise HTTPException(status_code=400, detail="Type can be only schedule and api!")
    
    if trigger.trigger_type == "time":
        if trigger.interval not in ["once", "hourly", "daily", "monthly"]:
            raise HTTPException(status_code=400, detail="Interval can be only hourly, daily and monthly!")

    url = f'{os.getenv("BASE_URL")}/api/pipelines/{trigger.name}/pipeline_schedules?api_key={os.getenv("API_KEY")}'
    headers = {
        "Authorization": f"Bearer {token.token}",
        "Content-Type": "application/json"
    }

    if trigger.trigger_type == "api":
        payload = json.dumps({
            "pipeline_schedule": {
                "name": trigger.trigger_name if trigger.trigger_name is not None else ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10)),
                "schedule_type": trigger.trigger_type,
                "status": "active"
            },
            "api_key": os.getenv("API_KEY")
        })
    else:
        payload = json.dumps({
            "pipeline_schedule": {
                "name": trigger.trigger_name if trigger.trigger_name is not None else ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10)),
                "schedule_type": trigger.trigger_type,
                "schedule_interval": "null" if trigger.interval is None else f"@{trigger.interval}",
                "start_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S%z') if trigger.start_time is None else trigger.start_time.strftime('%Y-%m-%d %H:%M:%S%z')
            },
            "api_key": os.getenv("API_KEY")
        })

    response = requests.request("POST", url, headers=headers, data=payload)

    if response.status_code != 200 or response.json().get("error") is not None:
        raise HTTPException(status_code=500, detail=response.json().get("error")["exception"])

    return JSONResponse(status_code=200, content="Trigger created successfully!")


@router.post("/mage/pipeline/run", tags=["PIPELINES POST"])
async def run_pipeline(pipe: Pipeline):
    if token.check_token_expired():
        token.update_token()
    if token.token == "":
        raise HTTPException(status_code=500, detail="Could not get the token!")

    url = f"{os.getenv('BASE_URL')}/api/pipeline_schedules/{pipe.run_id}/api_trigger"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {pipe.token}"
    }

    body = {
        "pipeline_run": {
            "variables": {

            }
        }
    }
    for k, v in pipe.variables.items():
        body['pipeline_run']['variables'][k] = v

    response = requests.post(url, headers=headers, json=body)

    if response.status_code != 200 or response.json().get("error") is not None:
        raise HTTPException(status_code=500, detail=response.json().get("error")["exception"])

    return JSONResponse(status_code=201, content="Pipeline Started Successfully!")


@router.post("/mage/pipeline/variables", tags=["PIPELINES POST"])
async def create_variables(variables: Variables):
    if token.check_token_expired():
        token.update_token()
    if token.token == "":
        raise HTTPException(status_code=500, detail="Could not get the token!")
    
    if len(variables.variables.keys()) == 0:
        raise HTTPException(status_code=400, detail="Should be at least one variable!")
    
    error_counter = 0
    
    for k, v in variables.variables.items():

        url = f'{os.getenv("BASE_URL")}/api/pipelines/{variables.name}/variables?api_key={os.getenv("API_KEY")}'

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token.token}",
            "X-API-KEY": os.getenv("API_KEY")
        }

        data = {
            "variable": {
                "name": k,
                "value": v
            },
            "api_key": os.getenv("API_KEY")
        }

        payload = json.dumps(data, indent=4)

        response = requests.request("POST", url, headers=headers, data=payload)

        if response.status_code != 200:
            error_counter += 1

    if error_counter > 0:
        raise HTTPException(status_code=500, detail=f"{error_counter} variables could not be created!")

    return JSONResponse(status_code=200, content="Variables added successfully!")


@router.post("/mage/pipeline/import", tags=["PIPELINES POST"])
async def import_pipeline(file: UploadFile):
    if file.content_type != "application/zip":
        raise HTTPException(status_code=500, detail="Only zip files are allowed!")
    
    if token.check_token_expired():
        token.update_token()
    if token.token == "":
        raise HTTPException(status_code=500, detail="Could not get the token!")

    headers = {
        "Authorization": f"Bearer {token.token}",
        "accept": "application/json",
    }

    url = f"{os.getenv('BASE_URL')}/api/files?api_key={os.getenv('API_KEY')}"

    file_content = await file.read()
    
    files = {
        "file": (file.filename, file_content, file.content_type),
        "json_root_body": (
            None,
            '{"api_key":"%s","dir_path":"","pipeline_zip":true,"overwrite":false}' % os.getenv('API_KEY'),
        ),
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, files=files)

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Error encountered when importing the pipeline!")

    return JSONResponse(status_code=200, content="Pipeline imported sucessfully!")


@router.post("/mage/pipeline/secret", tags=["PIPELINES POST"])
async def create_secret(secret: Secret):
    if token.check_token_expired():
        token.update_token()
    if token.token == "":
        raise HTTPException(status_code=500, detail="Could not get the token!")
    
    url = f'{os.getenv("BASE_URL")}/api/secrets?api_key={os.getenv("API_KEY")}'

    headers = {
        "Authorization": f"Bearer {token.token}",
        "Content-Type": "application/json",
        "X-API-KEY": os.getenv("API_KEY")
    }

    body = {
        "secret": {
            "name": secret.name,
            "value": secret.value
        },
        "api_key": os.getenv("API_KEY")
    }

    response = requests.request("POST", url, headers=headers, json=body)

    if response.status_code != 200 or response.json().get("error") is not None:
        raise HTTPException(status_code=500, detail=response.json().get("error")["exception"])
    
    return JSONResponse(status_code=200, content="Secret created successfully!")
