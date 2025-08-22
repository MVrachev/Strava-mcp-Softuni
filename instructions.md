# Начален setup #

1. Логваме се в Strava https://www.strava.com/dashboard
2. Цъкаме Settings ->  My API Application
3. Създаваме нашия Application
4. Копираме си и записваме като env variables:
- `Client ID`
- `Client Secret`

5. Пускаме си от терминал `src/setup_once.py` скрипта и следваме инструкциите му
6. От терминала копираме `**Refresh Token**` и го запазваме като env variable

# Стартиране на сървъра

Стартираме сървъра с:
```bash
docker compose up
```

# Интеграция с Cursor
1. Избираме Cursor -> Settings -> Cursor Settings -> Tools & Integrations -> New MCP Server
2. В JSON-а, който се отвори добавяме:

```json
{
  "mcpServers": {
    "strava-mcp-server": {
      "command": "npx",
      "args": [
        "-y",
        "supergateway",
        "--streamableHttp",
        "http://0.0.0.0:8000/mcp"
      ]
    }
  }
}
```

## Рестарт на сървъра с Cursor
1. Избираме Cursor -> Settings -> Cursor Settings -> Tools & Integrations -> цъкаме toggle на `strava-mcp-server` да е `OFF`
2. В терминала Control + C или спираме от Docker Desktop контейнера.
3. Правим промените, които искаме
4. От терминала:
```bash
docker compose up
```
5. Избираме Cursor -> Settings -> Cursor Settings -> Tools & Integrations -> цъкаме toggle на `strava-mcp-server` да е `ON`


# Интеграция с Clade Code
1. Избираме Claude -> Settings -> Developer -> Edit Configs -> Отворете `claude_desktop_config.json` с editor
2. В JSON-а, който се отвори добавяме:

```json
{
  "mcpServers": {
    "strava-mcp-server": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "http://0.0.0.0:8000/mcp",
        "--allow-http"
      ]
    }
  }
}
```

## Рестарт на сървъра с Claude Desktop
1. Спираме Claude Desktop
2. В терминала Control + C или спираме от Docker Desktop контейнера
3. Правим промените, които искаме
4. От терминала:
```bash
docker compose up
```
5. Стартираме Claude Desktop, ако няма грешки след стартиране, всичко точно.
6. Цъкаме бутона отдясно на `+` бутона под чат прозореца и трябва да видим `strava-mcp-server`
   с toggle `ON`


# Промптове:

## Strava MCP примерни промптове:
```
Give me insights based on my latest 100 activities and tell me which of those
do you think I put most effort in.
```

```
How is my running going as you look at my last 200 trainings?
Do I improve?
Do I degrade?
```

```
Do I have favourite weekdays for trainings?
```

```
Have a look at all my activities and tell me which period is the best one.
```


## Промптове при интеграция s Google calendar и нашия Strava MCP са добавени в Claude Code:
```
I want you to create a training program for me for a race happening on october 12-th.
I want to have one rest run, one fast run and one long run.
Base your plan on my current schedule from my calendar and my past strava activities
```
