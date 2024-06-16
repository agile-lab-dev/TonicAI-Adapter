<p align="center">
    <a href="https://www.witboost.com">
        <img src="docs/img/witboost_logo.svg" alt="witboost" width=600 >
    </a>
</p>

Designed by [Agile Lab](https://www.agilelab.it/), witboost is a versatile platform that addresses various sophisticated data engineering challenges. It enables businesses to discover, enhance, and productize their data, fostering the creation of automated data platforms that adhere to the highest standards of data governance. Want to know more about witboost? Check it out [here](https://www.witboost.com) or [contact us!](https://witboost.com/contact-us)

This repository is part of our [Starter Kit](https://github.com/agile-lab-dev/witboost-starter-kit) meant to showcase witboost's integration capabilities and provide a "batteries-included" product.

# Tonic AI Adapter

- [Overview](#overview)
- [Building](#building)
- [Running](#running)
- [OpenTelemetry Setup](specific-provisioner/docs/opentelemetry.md)
- [Deploying](#deploying)
- [API specification](docs/API.md)

## Overview

This project provides integration between Witboost and [Tonic.AI](https://www.tonic.ai/) to automatically generate a synthetic output port starting from the real one. 

![image]()

<img src="https://github.com/agile-lab/TonicAI-Adapter/assets/1837799/bf263496-075f-4152-9090-6cb9cabe479e" alt="image" width="500"/>

### Details

Access control is required to protect real output ports. A consumer must request access and wait for approval.
Witboost can automate the creation of a fake output port containing synthetic data, and this output port can be left without access management, so it will be super easy for a consumer to get a preview of the data and also start a prototype without waiting for its access granting to the real output port

<img src="https://github.com/agile-lab/TonicAI-Adapter/assets/1837799/36c0e332-b4d3-4579-9170-dd11b8709b45" alt="image"/>


## Building

**Requirements:**

- Python 3.11
- Poetry

**Installing**:

To set up a Python environment we use [Poetry](https://python-poetry.org/docs/):

```
curl -sSL https://install.python-poetry.org | python3 -
```

Once Poetry is installed and in your `$PATH`, you can execute the following:

```
poetry --version
```

If you see something like `Poetry (version x.x.x)`, your install is ready to use!

Install the dependencies defined in `specific-provisioner/pyproject.toml`:
```
cd specific-provisioner
poetry install
```

*Note:* All the following commands are to be run in the Poetry project directory with the virtualenv enabled.

**Type check:** is handled by mypy:

```bash
poetry run mypy src/
```

**Tests:** are handled by pytest:

```bash
poetry run pytest --cov=src/ tests/. --cov-report=xml
```

**Artifacts & Docker image:** the project leverages Poetry for packaging. Build package with:

```
poetry build
```

The Docker image can be built with:

```
docker build .
```

More details can be found [here](specific-provisioner/docs/docker.md).

*Note:* the version for the project is automatically computed using information gathered from Git, using branch name and tags. Unless you are on a release branch `1.2.x` or a tag `v1.2.3` it will end up being `0.0.0`. You can follow this branch/tag convention or update the version computation to match your preferred strategy.

**CI/CD:** the pipeline is based on GitLab CI as that's what we use internally. It's configured by the `.gitlab-ci.yaml` file in the root of the repository. You can use that as a starting point for your customizations.

## Running

To run the server locally, use:

```bash
cd specific-provisioner
source $(poetry env info --path)/bin/activate # only needed if venv is not already enabled
uvicorn src.main:app --host 127.0.0.1 --port 8091
```

By default, the server binds to port 8091 on localhost. After it's up and running, you can make provisioning requests for this address. You can also check the API documentation served [here](http://127.0.0.1:8091/docs).

## Env Variables

In order to set the application, some environmental variables must be injected:
- WorkspaceId: For this prototype, the workspace will be one, but potentially would be better to have one workspace for data product
- TonicAI API Key: you can retrieve it from your account setting panel of Tonic.AI

```python
workspaceId = os.getenv('WorkspaceId')
apiKey = os.getenv('API_KEY')
```

## Deploying

This microservice is meant to be deployed to a Kubernetes cluster with the included Helm chart and the scripts that can be found in the `helm` subdirectory. You can find more details [here](helm/README.md).

## License

This project is available under the [Apache License, Version 2.0](https://opensource.org/licenses/Apache-2.0); see [LICENSE](LICENSE) for full details.

## About us

<p align="center">
    <a href="https://www.witboost.com">
        <img src="docs/img/witboost_logo.svg" alt="Witboost" width=600>
    </a>
</p>

From Chaos to Control: Data Experience on Guardrails
Craft your own standards and automate your data practice

[Contact us](https://witboost.com/contact-us) or follow us on:
- [LinkedIn](https://www.linkedin.com/showcase/witboost/)
- [Instagram](https://www.instagram.com/agilelab_official/)
- [YouTube](https://www.youtube.com/channel/UCTWdhr7_4JmZIpZFhMdLzAA)
- [Twitter](https://twitter.com/agile__lab)
