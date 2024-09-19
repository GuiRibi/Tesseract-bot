import google.generativeai as genai
import discord
import os

class GeminiApi:
    def __init__(self, TOKEN, model):
        self.GEMINI_TOKEN = TOKEN
        self.model = model

        genai.configure(api_key=self.GEMINI_TOKEN)

        self.gemini = genai.GenerativeModel(self.model)
        self.chat = self.gemini.start_chat()

    async def ai(self, cmd, prompt, private):
        await cmd.response.defer(ephemeral=private)

        answer = self.chat.send_message(prompt, stream=True)
        
        full_response = ""
        message = None
        
        for chunk in answer:
            full_response += chunk.text
            embed = discord.Embed(description=full_response[:4096])  # Embed description limit is 4096
            
            if message is None:
                message = await cmd.followup.send(embed=embed, ephemeral=True)
            else:
                await message.edit(embed=embed)
            
            if len(full_response) >= 4096:
                break  # Stop if we exceed the embed limit
        
        if len(full_response) > 4096:
            await cmd.followup.send("Response exceeded maximum length. Here's the truncated version.", ephemeral=True)
        
        if message is None:
            await cmd.followup.send("No response received from the AI.", ephemeral=True)
