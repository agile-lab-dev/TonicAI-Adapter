from datetime import datetime
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, RootModel, Field
import json

import sys
import os

from requests.auth import HTTPBasicAuth
import requests
import yaml

from starlette.responses import Response
import asyncio 

from src.utility.parsing_pydantic_models import parse_yaml_with_model

workspaceId = os.getenv('workspaceId')
apiKey = os.getenv('API_KEY')
headers = {'Accept': 'application/json', 'Authorization': f'ApiKey {apiKey}'}
print(headers)

class Column(BaseModel):
    schema: str
    table: str
    columnName: str
    dataType: str
    simpleDataType: str
    customTypeDetails: List = []
    dateTimeSubsetType: str
    isNullable: bool
    hasDefaultValue: bool
    keyType: str
    keyOrder: int
    isTargetOfUserDefinedForeignKey: bool
    isUnique: bool
    disabledForScaleUp: bool
    allowedGeneratorCacheKey: str
    allowedSubGeneratorCacheKey: str
    suggestedGeneratorCacheKey: str
    maxCharacterLength: int
    identityType: str

class SchemaAndTable(BaseModel):
    schema: str
    table: str

class Table(BaseModel):
    tableName: str
    schemaOfTable: str
    columns: List[Column]
    rowCountEstimate: int
    pageCountEstimate: int
    tableSizeMegabytes: float
    isMemoryOptimized: bool
    isIndexOrganized: bool
    isPartitioned: bool
    inheritanceFromSpecifier: str
    isView: bool
    temporalType: str
    schemaAndTable: SchemaAndTable
    debuggerDisplay: str

class WorkspaceTables(BaseModel):
    tables: List[Table]
    databaseSizeMegabytes: float
    allowedGeneratorCache: Dict[str, List[str]]
    suggestedGeneratorCache: Dict[str, List[str]]




class PrivacyColumn(BaseModel):
    dataType: str
    isIncluded: bool
    isSensitive: bool
    tonicDetectedSensitivity: bool
    sensitiveType: Optional[str]
    isProtected: bool
    columnProtection: str
    generator: str
    isDifferentiallyPrivate: bool
    isDataFree: bool
    isConsistent: bool
    consistencyColumn: str
    privacyStatus: str
    privacyRank: str
    column: str
    schema: str
    table: str

class PrivacyTable(BaseModel):
    tableMode: str
    columns: Dict[str, Column]
    privacyStatus: str
    tableProtection: str
    schema: str
    table: str

class ColumnCountByPrivacyRank(BaseModel):
    One: int
    Two: int
    Three: int
    Four: int
    Five: int
    Six: int

class PrivacyData(BaseModel):
    tables: Dict[str, Table]
    notIncludedColumnCount: int
    notSensitiveColumnCount: int
    atRiskColumnCount: int
    protectedColumnCount: int
    columnCountByPrivacyRank: ColumnCountByPrivacyRank
    notIncludedTableCount: int
    notSensitiveTableCount: int
    atRiskTableCount: int
    protectedTableCount: int
    partiallyMaskedTableCount: int
    fullyMaskedTableCount: int
    anonymizedTableCount: int

class Generator(BaseModel):
    generatorId: str
    generatorLabel: str
    description: Optional[str]
    searchTerm: List[str]
    canPartition: bool
    canPartitionBy: bool
    canBeDifferentiallyPrivate: bool
    canLink: bool
    canBeConsistent: bool
    canBeConsistentOn: bool
    mustBeConsistentOnUniqueColumn: bool
    canScale: bool
    preferJavaUdf: bool
    hasFallback: bool
    fallbackGeneratorIds: List[str]
    isImplicitlyConsistent: bool
    isProcessHeavy: bool

class Generators(RootModel[List[Generator]]):
    pass

    

class Link(BaseModel):
    column: str
    table: str
    schema: str
    metadata: dict



class Replacement(BaseModel):
    name: str
    links: List[Link]
    fallbackLinks: List = Field(default_factory=list)
    table: str
    schema: str
    partitions: List = Field(default_factory=list)
    nnModelConfig: Optional[dict] = None

class Replacements(RootModel[Dict[str, Replacement]]):
    pass


def buildReplacement(schemaComp, tableComp, column, generatorId):
    replacement = Replacement(
        name = column,
        links = [
            Link(
                column = column,
                table = tableComp,
                schema = schemaComp,
                metadata = {
                    "generatorId": f"{generatorId}",
                    "presetId": f"{generatorId}",
                    "isDifferentiallyPrivate": False
                }
            )
        ],
        fallbackLinks = [],
        table = tableComp,
        schema = schemaComp,
        partitions = [],
        nnModelConfig = {
            "modelType": "VAE",
            "epochs": 0,
            "batchSize": 0,
            "earlyStopping": True,
            "recLossFactor": 0,
            "latentDim": 0,
            "maxCategoricalDim": 0,
            "encoderLayerSizes": [
            0
            ],
            "decoderLayerSizes": [
            0
            ],
            "rnnEncoderHiddenSize": 0,
            "rnnDecoderHiddenSize": 0,
            "rnnDecoderFullyConnectedSize": 0,
            "uiSequenceLength": 0,
            "maxOrderDimension": 0,
            "maskLossFactor": 0,
            "orderLossFactor": 0
        }
    )



def getTablesFromWorkspace() -> WorkspaceTables:
    tablesUrl = f'https://app.tonic.ai/api/table?workspaceId={workspaceId}'
    
    response = requests.get(tablesUrl, headers=headers)
    print(response.content)
    # Parse the JSON string
    yamlparsed: dict = yaml.safe_load(response.content)
    tonicTables_response = parse_yaml_with_model(yamlparsed, WorkspaceTables)
    print(tonicTables_response)
    return tonicTables_response

def getPrivayAnalysis():
    tablesUrl = f'https://app.tonic.ai/api/Privacy/analysis?workspaceId={workspaceId}&api-version=v2024.01.0'
    
    response = requests.get(tablesUrl, headers=headers)
    print(response.content)
    # Parse the JSON string
    yamlparsed: dict = yaml.safe_load(response.content)
    tonicPrivacy_response = parse_yaml_with_model(yamlparsed, PrivacyData)
    print(tonicPrivacy_response)
    return tonicPrivacy_response

def getGenerators():
    tablesUrl = f'https://app.tonic.ai/api/GeneratorMetadata?api-version=v2024.01.0'
    
    response = requests.get(tablesUrl, headers=headers)
    print(response.content)
    # Parse the JSON string
    yamlparsed: dict = yaml.safe_load(response.content)
    tonicGenerators_response = parse_yaml_with_model(yamlparsed, Generators)
    #print(tonicGenerators_response)
    return tonicGenerators_response

def getTableReplacements(schema, table):
    tablesUrl = f'https://app.tonic.ai/api/Workspace/{workspaceId}/replacements/{schema}/{table}?api-version=v2024.01.0'
    
    response = requests.get(tablesUrl, headers=headers)
    print(response.content)
    # Parse the JSON string
    yamlparsed: dict = yaml.safe_load(response.content)
    tonicReplacements_response = parse_yaml_with_model(yamlparsed, Replacements)
    #print(tonicReplacements_response)
    return tonicReplacements_response

def updateReplacements(schema, table, replacements):
    tablesUrl = f'https://app.tonic.ai/api/Workspace/{workspaceId}/update_replacements/{schema}/{table}?api-version=v2024.01.0'
    
    json_data = {
        "replacements": replacements
    }

    response = requests.put(tablesUrl, json=json_data,headers=headers)
    response.raise_for_status()
    created_object = yaml.safe_load(response.content)
   
    return created_object


def setSensitiveColumns(schema, table, columns):

    tablesUrl = f'https://app.tonic.ai/api/Privacy/set?api-version=v2024.01.0'

    columnKeys = []
    for column in columns:
        columnKeys.append({
            "schema": schema,
            "table": table,
            "columnName": column
        })

    data = {
        "columnKeys": columnKeys,
        "workspaceId": workspaceId
    }

    response = requests.post(tablesUrl, json=data, headers=headers)
    response.raise_for_status()
    created_object = yaml.safe_load(response.content)
    return created_object

def generate_data(replacements, columns):
        generate_data_url = f'https://app.tonic.ai/api/generateddata'
        
        columndict = {}
        for col in columns:
            columndict[col] = []

        json_data = {
            "replacements": list(replacements.values()),
            "workspaceId": workspaceId,
            "isScaled": True,
            "dirtyColumns": columns,
            "data": columndict
        }


        r = requests.post(generate_data_url, json=json_data, headers=headers)
        r.raise_for_status()

        return r.content


