# Telegram-Muter

Apart from muting chats in Telegram, this script will read messages in specific chats that you choose.
It updates the messages counter in those, like if you have read them, so you won't get these annoyinng counters on some chats.

# To set up:
1. Clone repo
2. Change config: 
  1. Enter your phone number
  2. Auth Password (if you have one)
  3. API ID and API HASH (<a href='https://my.telegram.org/auth'> Go here</a> to create an app and get these)
3. Run <code>setup.py</code> <b>ONCE</b> to create a db.
4. Run script <code>main_ch.py</code> and enter code you will receive.
5. Use the script on your VPS to read the messages 24/7

# To mute:
Send message <code>!mute</code> to the chat you want to mute
You will receive the message in the Saved Messages that the chat is muted


# To unmute:
Send message <code>!unmute</code> to the chat you want to unmute
You will receive the message in the Saved Messages that the chat is unmuted
