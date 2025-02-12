# CityMood

## Test locally with VS Code

### Setup environment
 - Clone repo and `cd` into
 - Create python virtual environment : `python -m venv .venv`
 - Activate virtual env : `.venv\Scripts\activate`
 - Install python libs : `pip install -r .\requirements.txt`
 - Copy `example.env` and rename to `.env`
 - Edit env variables

### Install ODBC Drive for SQL
 - https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server?view=sql-server-ver16

## Update `requirements.txt`
`pipreqs src --force --mode no-pin --savepath requirements.txt`

## Build Docker image, push to Azure registry and update container app

### Prerequisites
 - Docker installed and running
 - Azure CLI installed : `winget install -e --id Microsoft.AzureCLI`

### Execute the script
 - `.\build-and-push-to-azure-registry.ps1`
