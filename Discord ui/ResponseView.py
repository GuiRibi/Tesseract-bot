import discord
from discord import ui

class ResponseView(ui.View):
    def __init__(self, pages):
        super().__init__()
        self.pages = pages
        self.current_page = 0

    @ui.button(label="Next Page", style=discord.ButtonStyle.primary)
    async def next_page(self, interaction: discord.Interaction, button: ui.Button):
        self.current_page = (self.current_page + 1) % len(self.pages)
        await interaction.response.edit_message(content=self.pages[self.current_page], view=self)