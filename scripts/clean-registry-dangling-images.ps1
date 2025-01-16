# Ce script permet de nettoyer un registre Azure Container Registry (ACR) en
# supprimant les images non étiquetées (dangling images), tout en conservant
# les 3 plus récentes.

# Définit une variable contenant le nom du registre Azure Container Registry (ACR)
$ACR_NAME = "citymood"

# Exécute une commande dans le contexte du registre ACR spécifié
az acr run --registry $ACR_NAME --cmd "acr purge --filter '*:.*' --ago 0d --keep 3 --untagged" /dev/null
