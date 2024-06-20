from __future__ import annotations

from requests.auth import HTTPBasicAuth
import requests
import uuid

import sys
import os

import yaml
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

import asyncio 


from src.dependencies import unpack_provisioning_request
from src.utility.parsing_pydantic_models import parse_yaml_with_model

from starlette.responses import Response

from src.app_config import app
from src.check_return_type import check_response
from src.models.api_models import (
    ProvisioningRequest,
    ProvisioningStatus,
    SystemErr,
    UpdateAclRequest,
    ValidationError,
    ValidationRequest,
    ValidationResult,
    ValidationStatus,
)

from src.models.tonic import *
from src.models.data_product_descriptor import *

from src.utility.logger import get_logger

logger = get_logger()


@app.post(
    "/v1/provision",
    response_model=None,
    responses={
        "200": {"model": ProvisioningStatus},
        "202": {"model": str},
        "400": {"model": ValidationError},
        "500": {"model": SystemErr},
    },
    tags=["SpecificProvisioner"],
)
async def provision(
    body: ProvisioningRequest,
) -> Response:
    """
    Deploy a data product or a single component starting from a provisioning descriptor
    """

    # get data from tonic workspace
    workspaceTables = getTablesFromWorkspace()
    
    dp = await unpack_provisioning_request(body)
    print("------------------DESCRIPTOR PARSED-----------------------------")
    print(dp)
    
    generators = getGenerators()
    print("------------------GENERATORS-----------------------------")
    for generator in generators.root:
        print(generator.generatorId)

    for component in dp[0].components:
        if component.kind == "outputport":
            cdict: dict = component.dict()
            rename_key(cdict['dataContract'], 'schema_', 'schema')
            outputport = OutputPort(**cdict)
            tableComp = outputport.specific["table"]
            schemaComp = outputport.specific["schema"]
            

            for table in workspaceTables.tables:
                if table.tableName == tableComp and table.schemaOfTable == schemaComp:
                    #replacements = getTableReplacements(schemaComp, tableComp)
                    columns = outputport.dataContract.schema_
                    print(columns)

                    columnKeys = []
                    sensitiveColumns = []
                    replacements = []
                    for column in columns:
                        columnKeys.append(column.name)
                        if column.tags != None:
                            for tag in column.tags:
                                if tag.tagFQN != None and ( tag.tagFQN == "PII" or tag.tagFQN == "Sensitive" ):
                                    sensitiveColumns.append(column.name)
                        
                        if column.masking != None:
                            #print(generators.root)
                            for generator in generators.root:
                                #print(generator.generatorId)
                                #print(column.masking.generatorType)
                                if generator.generatorId == (""+column.masking.generatorType + "Generator"):
                                    print(" generator found: " + generator.generatorId)

                                    replacement = buildReplacement(schemaComp, tableComp, column.name, generator.generatorId)
                                    replacement.links[0].metadata = customizeMetadata(replacement.links[0].metadata, generator.generatorId, column)
                                           
                                    replacements.append(replacement)
                                    print("new replacement")
                                    print(replacement)
                        else:

                            replacement = buildReplacement(schemaComp, tableComp, column.name, "PassthroughGenerator")
                            replacements.append(replacement)

                    setSensitiveColumns(schemaComp, tableComp, sensitiveColumns)

                    updated_replacements_dict: Dict[str, dict] = {}
                    
                    for replacement in replacements:
                        key = f"{uuid.uuid4()}"
                        updated_replacements_dict[key] = replacement.dict()
                    
                    print(json.dumps(updated_replacements_dict, indent=4))

                    updateReplacements(schemaComp, tableComp, updated_replacements_dict)

                    generate_data(updated_replacements_dict, columnKeys)




    resp = ProvisioningStatus(status="", result="")

    return check_response(out_response=resp)

def customizeMetadata(metadata, generatorId, column):
    match generatorId:
        case "NameGenerator":
            metadata.update({
                "preserveCapitalization": False,
                "nameType": f'{column.masking.specific["part"]}'
            })
        case "CategoricalGenerator":
            metadata.update({
                "epsilon": 1,
                "turinBound": 0
            })
        case "EmailGenerator":
            metadata.update({
                "replaceInvalidEmails": False,
                "turinBound": 0
            })
        case "RandomTimestampGenerator":
            metadata.update({
                "minDate": "2024-06-17T23:49:09.3138384Z",
                "maxDate": "2024-06-19T23:49:09.3138393Z",
                "minTime": "2024-06-17T23:49:09.3138365Z",
                "maxTime": "2024-06-19T23:49:09.3138374Z",
                "dateTimeFormat": "yyyy-MM-ddTHH:mm:ss",
                "unixTimestampFormat": "Seconds",
            })
        case "RandomIntegerGenerator":
            metadata.update({
                "min": column.masking.specific["minimum"],
                "max": column.masking.specific["maximum"]
            })

    return metadata


@app.get(
    "/v1/provision/{token}/status",
    response_model=None,
    responses={
        "200": {"model": ProvisioningStatus},
        "400": {"model": ValidationError},
        "500": {"model": SystemErr},
    },
    tags=["SpecificProvisioner"],
)
def get_status(token: str) -> Response:
    """
    Get the status for a provisioning request
    """



    # todo: define correct response
    resp = SystemErr(error="Response not yet implemented")

    return check_response(out_response=resp)


@app.post(
    "/v1/unprovision",
    response_model=None,
    responses={
        "200": {"model": ProvisioningStatus},
        "202": {"model": str},
        "400": {"model": ValidationError},
        "500": {"model": SystemErr},
    },
    tags=["SpecificProvisioner"],
)
def unprovision(
    body: ProvisioningRequest,
) -> Response:
    """
    Undeploy a data product or a single component
    given the provisioning descriptor relative to the latest complete provisioning request
    """  # noqa: E501

    # todo: define correct response
    resp = SystemErr(error="Response not yet implemented")

    return check_response(out_response=resp)


@app.post(
    "/v1/updateacl",
    response_model=None,
    responses={
        "200": {"model": ProvisioningStatus},
        "202": {"model": str},
        "400": {"model": ValidationError},
        "500": {"model": SystemErr},
    },
    tags=["SpecificProvisioner"],
)
def updateacl(
    body: UpdateAclRequest,
) -> Response:
    """
    Request the access to a specific provisioner component
    """

    # todo: define correct response
    resp = SystemErr(error="Response not yet implemented")

    return check_response(out_response=resp)


@app.post(
    "/v1/validate",
    response_model=None,
    responses={"200": {"model": ValidationResult}, "500": {"model": SystemErr}},
    tags=["SpecificProvisioner"],
)
def validate(body: ProvisioningRequest) -> Response:
    """
    Validate a provisioning request
    """

    # todo: define correct response
    resp = SystemErr(error="Response not yet implemented")

    return check_response(out_response=resp)


@app.post(
    "/v2/validate",
    response_model=None,
    responses={
        "202": {"model": str},
        "400": {"model": ValidationError},
        "500": {"model": SystemErr},
    },
    tags=["SpecificProvisioner"],
)
def async_validate(
    body: ValidationRequest,
) -> Response:
    """
    Validate a deployment request
    """

    # todo: define correct response
    resp = SystemErr(error="Response not yet implemented")

    return check_response(out_response=resp)


@app.get(
    "/v2/validate/{token}/status",
    response_model=None,
    responses={
        "200": {"model": ValidationStatus},
        "400": {"model": ValidationError},
        "500": {"model": SystemErr},
    },
    tags=["SpecificProvisioner"],
)
def get_validation_status(
    token: str,
) -> Response:
    """
    Get the status for a provisioning request
    """

    # todo: define correct response
    resp = SystemErr(error="Response not yet implemented")

    return check_response(out_response=resp)

def rename_key(dictionary, old_key, new_key):
    if old_key in dictionary:
        dictionary[new_key] = dictionary.pop(old_key)
    else:
        raise KeyError(f"Key '{old_key}' not found in dictionary")
