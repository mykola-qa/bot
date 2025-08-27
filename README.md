# bot 
Bot with integration to Open AI and Telegram API

# docker server pi4
docker build . -t bot-app 
docker run -d --restart unless-stopped \
  --name bot-app \
  --env-file .env \
  -p 5000:5000 \
  -v /home/pi/codenoim/bot/sql_lite_db/:/usr/src/app/sql_lite_db/ \
  bot-app

# docker running on my local pc
docker run -d --restart unless-stopped --name bot-app --env-file .env -p 5000:5000 -v F:\codenoim\tg-bot\tg-bot\sql_lite_db\:/usr/src/app/sql_lite_db/ bot-app