# CityMood

## Test locally with VS Code

### Setup environment
 - Clone repo and `cd` into
 - Create python virtual environment : `python -m venv .venv`
 - Activate virtual env : `.venv\Scripts\activate`
 - Install python libs : `pip install -r .\requirements.txt`
 - Copy `example.env` and rename to `.env`
 - Edit env variables

### Setup Azure Function
 - Install VS Code extension [Azure Functions](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-azurefunctions)
 - Install or update Core Tools : F1 -> `Azure Functions : Install ou Update Core Tools`
 - Copy `example.local.settings.json` and rename to `local.settings.json`
 - Edit secrets
