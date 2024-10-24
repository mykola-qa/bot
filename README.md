# bot 
Bot with integration to Open AI and Telegram API

# docker
docker build . -t bot-app 
docker run -d --restart unless-stopped \
  --name bot-app \
  --env-file .env \
  -p 5000:5000 \
  -v /home/pi/codenoim/bot/sql_lite_db/:/usr/src/app/sql_lite_db/ \
  bot-app
