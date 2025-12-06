import os
import logging 
import discord
from discord import app_commands
from dotenv import load_dotenv
from litellm import completion
from litellm import text_completion
from litellm import OpenAIWebSearchOptions

load_dotenv()
os.environ["GEMINI_API_KEY"] = os.getenv("GOOGLE_GEMINI_KEY")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_KEY")

SLASH_COMMAND_NAME = "kkb"
SHORTHAND_COMMAND_PREFIX = "%"
CHAR_LIMIT_DISCORD = 2000         # max chars in a discord message

# DISCORD_KEY = os.getenv("DISCORD_TEST_KEY")
# PROXY = "socks5://127.0.0.1:1087"

DISCORD_KEY = os.getenv("DISCORD_KEY")
PROXY = None

models = [
    # "gemini/gemini-3-pro-preview",
    "gemini/gemini-2.5-pro",
    "gemini/gemini-2.5-flash",
    "gemini/gemini-2.0-flash",

    "openai/gpt-5.1", 
    "openai/gpt-5",   
    "openai/gpt-5-mini",
    "openai/gpt-4.1",

    "openai/davinci-002",
]

DEFAULT_MODEL = models[0]

logging.basicConfig(level = logging.INFO, format = "%(asctime)s %(levelname)s %(process)d %(message)s")

async def get_response(model, prompt, img_url, web_search, temperature):
    try:
        response = None

        if model == models[-1]:   # legacy completion model davinci-002
            response = text_completion(
                model = model,
                prompt = prompt,
                temperature = temperature,
                max_tokens = 1000
            )
            return response.choices[0].text
        
        else:  
            response = completion(
                model = model,
                messages=[
                    { "role": "developer", "content": "Be concise." },
                    {
                        "role": "user", 
                        "content": [
                            { "type": "text", "text": prompt },
                            *( [{ "type": "image_url", "image_url": img_url }] if img_url else {} ) 
                        ]
                    }
                ],
                # tools=[{ "type": "web_search_preview" }] if web_search else [],
                # max_tokens = 1000
            ) 
            return response.choices[0].message.content
    
    except Exception as e:
        logging.error(str(e))
        return "612,842,912,135 DEMOLISHED DATA CENTERS: " + str(e) 

async def send_msg(model, followup, prompt, img_url, web_search, temperature, is_shorthand = False):
    try:
        response = await get_response(model, prompt, img_url, web_search, temperature)    

        if len(response) > CHAR_LIMIT_DISCORD:
            parts = [response[i:i+CHAR_LIMIT_DISCORD] for i in range(0, len(response), CHAR_LIMIT_DISCORD)]
            for part in parts:
                if is_shorthand == True:
                    await followup.reply(part)
                else:
                    await followup.send(part)
        else:
            if is_shorthand == True:
                await followup.reply(response)
            else:
                await followup.send(response)

    except Exception as e:
        logging.error(str(e))
        if is_shorthand == True:
            await followup.reply(str(e))
        else:
            await followup.send(str(e))

def run_discord_bot():
    intents = discord.Intents.default()
    intents.message_content = True

    bot = discord.Client(intents = intents, proxy = PROXY) 
    tree = app_commands.CommandTree(bot)

    @bot.event
    async def on_ready():
        try:
            synced = await tree.sync()
            logging.info(f"synced {len(synced)} commands")
        except Exception as e:
            logging.error(f"failed to sync command tree: {str(e)}")

    # slash command  
    @tree.command(name = SLASH_COMMAND_NAME) 
    @app_commands.choices(model = [
        # app_commands.Choice(name = "gemini/gemini-3-pro-preview", value = 0),
        app_commands.Choice(name = "gemini/gemini-2.5-pro", value = 0),
        app_commands.Choice(name = "gemini/gemini-2.5-flash", value = 1),
        app_commands.Choice(name = "gemini/gemini-2.0-flash", value = 2),
        app_commands.Choice(name = "openai/gpt-5.1", value = 3),
        app_commands.Choice(name = "openai/gpt-5", value = 4),
        app_commands.Choice(name = "openai/gpt-5-mini", value = 5),
        app_commands.Choice(name = "openai/gpt-4.1", value = 6),
        app_commands.Choice(name = "openai/davinci-002", value = 7)
    ])
    async def on_command(
        interaction: discord.Interaction,
        model: app_commands.Choice[int],
        prompt: str,
        img_url: str = None,
        web_search: bool = False,
        temperature: float = 1.0,
        ):

        # temperature is between 0 and 2
        temperature = max(min(temperature, 2), 0)
          
        if img_url == None:
            await interaction.response.send_message(f"retard really said \"{prompt}\" to {model.name} ")
        else:
            await interaction.response.send_message(f"retard really said \"{prompt}\" and sent this image {img_url} to {model.name}")

        # print(f'\n✧･ﾟ:✧･ﾟ:* ✧･ﾟ✧*:･ﾟﾐ☆ \n sending prompt "{prompt}" and image {img_url} to model {model.name} at temperature {temperature} \n ✧･ﾟ:✧･ﾟ:* ✧･ﾟ✧*:･ﾟﾐ☆')
        await send_msg(model.name, interaction.followup, prompt, img_url, web_search, temperature, False)

    # shorthand command for the default model
    @bot.event
    async def on_message(msg):
        # ignore dms and msg sent by the bot itself
        if msg.channel.type == "private" or msg.author == bot.user:
            return

        # ignore msg not starting with the command prefix
        if msg.content == None or len(msg.content) < 1 or msg.content[0] != SHORTHAND_COMMAND_PREFIX:
            return
        
        usr_msg = msg.content[1:]
        # print(f'\n✧･ﾟ:✧･ﾟ:* ✧･ﾟ✧*:･ﾟﾐ☆ \n sending prompt "{usr_msg}" to default model {DEFAULT_MODEL} \n ✧･ﾟ:✧･ﾟ:* ✧･ﾟ✧*:･ﾟﾐ☆')
        await send_msg(DEFAULT_MODEL, msg, usr_msg, None, False, 1.0, True)

    bot.run(DISCORD_KEY)

if __name__ == '__main__':
    run_discord_bot()