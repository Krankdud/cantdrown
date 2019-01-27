# cantdrown

Discord bot for a personal server. Used to host [Zandronum](https://wwww.zandronum.com) servers.

## Usage

```bash
git clone https://github.com/Krankdud/cantdrown
virtualenv venv
. venv/bin/activate
pip install -r requirements.txt
python bot.py <token>
```
token is your Discord bot token from the [Discord Developer Application Portal](https://discordapp.com/developers/applications/).

## Commands

```
!host <iwad> <idgames url> - Hosts a Zandronum server
```

## Configuration

### Doom

Edit the doom.json file in the config folder to configure the Zandronum server settings.

Setting | Explanation
------- | -----------
zandronum | Command to run Zandronum
serverArguments | Additional arguments to pass to the server (e.g. executing a config)
serverBaseName | Base name for the server. Servers are hosted with the name "\<serverBaseName\> (\<wad name\>)"
iwads | Object mapping the names of the iwad to the path of the iwad
wadsDirectory | Path to the directory where wads are stored
idgamesMirror | URL of an idgames archive mirror that is used to download wads