import discord
import os
from discord import app_commands
import replicate
import aiohttp
import asyncio
import io
REPLICATE_API_TOKEN = os.environ['REPLICATE_API_TOKEN'] # make an environmental variable that holds your https://replicat.com api key
replicate_client = replicate.Client(api_token=REPLICATE_API_TOKEN)
bot_token = os.environ['DISCORD_TOKEN'] # the discord bot token
intents = discord.Intents.none()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
@client.event
async def on_ready():
    await tree.sync()
    await client.change_presence(
        activity=discord.Activity(name="with DeepFloyd!", #the bot activity status
                                  type=discord.ActivityType.playing,
                                  details="IF"))
    print(f'Connected to Discord!')

@tree.command(name="imagine_if", description="Generate an image using DeepFloyd IF") # the command name and description
async def imagine_if(interaction: discord.Interaction, prompt: str, negative_prompt: str = "Deformed, ugly, artifacts"): #the default negative prompt values
    await interaction.response.defer(thinking=True)
    data = {
        "version": "639f0cd40c18b992715d00b8d489ff557c2e47de6c61be1fcc38a3c10cfb1ecd",
        "input": {
            "prompt": prompt,
            "negative_prompt": negative_prompt
        }
    }
    headers = {
        "Authorization": f"Token {REPLICATE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post("https://api.replicate.com/v1/predictions", headers=headers, json=data) as response:
            response_data = await response.json()
            prediction_id = response_data["id"]
            prediction_url = f"https://api.replicate.com/v1/predictions/{prediction_id}"
            
            while True:
                async with session.get(prediction_url, headers=headers) as prediction_response:
                    prediction_data = await prediction_response.json()
                    if prediction_data["status"] == "succeeded":
                        output = prediction_data["output"]
                        break

                await asyncio.sleep(2)
        image_url = output[0]
        async with session.get(image_url) as image_response:
            if image_response.status == 200:
                image_data = await image_response.read()
                image_file = io.BytesIO(image_data)
                
                embed = discord.Embed(title="Generated with IF", description=prompt)
                embed.set_image(url="attachment://generated_image.png")
                await interaction.followup.send(embed=embed, file=discord.File(image_file, "generated_image.png"))
                
            else:
                print("Failed to download image.")

client.run(bot_token)
