from discord.ext import commands

class DiscordBot(commands.Bot):
    def __init__(self, token, intents, **options):
        super().__init__(command_prefix="!", intents=intents, **options)
        self.token = token
        self.is_ready = False  # Flag pour indiquer si le bot est prêt

    async def send_message(self, channel_id, message):
         # Utiliser self.is_ready pour vérifier si le bot est connecté
        if not self.is_ready:
           print("Le bot n'est pas prêt à envoyer des messages.")
           return
        channel = self.get_channel(int(channel_id))
        if channel:
            print(f"Sendind '{message}' in channel {channel_id}")
            await channel.send(message)
        else:
            print(f"Channel {channel_id} not found")

    async def on_ready(self):
        print(f'{self.user} est connecté !')
        self.is_ready = True  # Mettre le flag à True quand le bot est prêt

    async def start_bot(self):
        try:
          await self.login(self.token) # Login du bot (ne démarre pas la boucle d'événement)
          await self.connect(reconnect=True) # Démarrer le bot et la boucle d'événements en arrière-plan.
        except Exception as e:
           print(f"Une erreur est survenue pendant le démarrage du bot : {e}")