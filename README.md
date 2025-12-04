# discord-llm-bot
simple discord bot that responds to messages using llm apis

## usage
#### slash command
`/kkb [model] [prompt] [image_url] [web_search] [temperature] `<br>
`model` and `prompt` are required, rest are optional<br>

#### shorthand command
`%[prompt]`<br>
talk to the default model gemini-2.5-pro

## setup and run
- create a venv and install requirements
  ```
  python3 -m venv .venv
  source .venv/bin/activate
  pip -r install requirements.txt
  ```
- create a .env file using the template below. paste your discord and openai keys
- if u wish to use the shorthand command, enable `message content intent` in the "Bot" section 
- go to OAuth2 - URL generator, set scopes to `bot` and `applications.commands`. select the `send messages` and `use slash commands` permissions
- invite the bot to your server with the link and run main.py

## .env
```
DISCORD_KEY="42069"
GOOGLE_GEMINI_KEY="123456"
OPENAI_KEY="654321"
```
