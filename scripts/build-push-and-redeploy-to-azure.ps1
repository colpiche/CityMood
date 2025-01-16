# Script PowerShell pour builder et pusher une image Docker vers un Azure Container Registry (ACR)
# puis redémarrer le container correspondant avec l'image à jour

$resourceGroup = "CityMood"
$acrName = "citymood"
$acrUrl = "$acrName.azurecr.io"
$imageName = "citymood-app"
$taggedImage = "$acrUrl/$imageName"
$containerApp = "ctrapp-citymood-prod-fr-01"

function Execute-Command {
    param (
        [Parameter(Mandatory = $true)]
        [string]$Command
    )

    # Afficher la commande interprétée
    Write-Host ">> $Command" -ForegroundColor Yellow

    try {
        # Exécuter la commande
        Invoke-Expression $Command

        # Vérifier si la commande a échoué
        if ($LASTEXITCODE -ne 0) {
            throw "La commande '$Command' a échoué avec le code de sortie $LASTEXITCODE."
        }
    } catch {
        Write-Host "Erreur : $_" -ForegroundColor Red
        exit 1
    }
}

# Connexion à Azure
Execute-Command "az login"

# Connexion au Azure Container Registry (ACR)
Execute-Command "az acr login --name $acrName"

# Construction de l'image Docker
Execute-Command "docker build -t $imageName ../"

# Tag de l'image pour le push vers ACR
Execute-Command "docker tag ${imageName}:latest $taggedImage"

# Push de l'image vers ACR
Execute-Command "docker push $taggedImage"

# Récupération automatique de la révision actuelle
$revision = az containerapp revision list --name $containerApp --resource-group $resourceGroup --query "[0].name" -o tsv

if ($revision) {
    Write-Host "Révision actuelle trouvée : $revision" -ForegroundColor Green

    # Redémarrage de la révision
    Execute-Command "az containerapp revision restart --name $containerApp --resource-group $resourceGroup --revision $revision"
} else {
    Write-Host "Aucune révision trouvée pour l'application $containerApp." -ForegroundColor Red
    exit 1
}

Write-Host "Processus terminé avec succès !" -ForegroundColor Green
