from discord.ext.commands import Cog

from database import DatabaseInteractor

class Reactions(Cog):
    def __init__(self, bot):
        self.bot = bot

    async def on_raw_reaction(self, payload):
        print("Reacted")

        if payload.emoji.name != "📌":
            return

    @Cog.listener()
    async def on_raw_reaction_add(self, payload):
        await self.on_raw_reaction(payload)

def setup(bot):
    bot.add_cog(Reactions(bot))
