from prodiapy import Prodia
import discord
import os

class ProdiaApi:
    def __init__(self, TOKEN):
        self.PRODIA_TOKEN = TOKEN
        self.prodia = Prodia(api_key=self.PRODIA_TOKEN)

    async def send_image(self, cmd, image_url):
        embed = discord.Embed()
        embed.set_image(url=image_url)
        return embed
    
    async def generate(self, cmd, prompt, private):
        await cmd.response.defer(ephemeral=private)
    
        prmp = prompt

        job = self.prodia.sd.generate(prompt=prmp)
        result = self.prodia.wait(job)

        await cmd.followup.send(embed= await self.send_image(cmd, result.image_url))
