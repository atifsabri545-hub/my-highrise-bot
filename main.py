import os
from flask import Flask
from threading import Thread
from highrise import BaseBot, Position
from highrise.models import SessionMetadata, User

# --- 24/7 ZINDA RAKHNE KE LIYE SERVER ---
app = Flask('')
@app.route('/')
def home():
    return "Bot is Running!"

def run_server():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_server)
    t.start()
# ---------------------------------------

class MyBot(BaseBot):
    # 🔐 OWNER
    owner = "The_Cora_King"

    # 👑 ROLES
    admins = ["The_Cora_King"]
    vips = []

    # 🌍 PUBLIC FLOORS
    public_floors = {
        "f1": Position(0, 0, 0),
        "f2": Position(5, 0, 5),
        "f3": Position(10, 0, 10)
    }

    vip_positions = {}
    admin_positions = {}
    emotes = {}

    async def on_start(self, session_metadata: SessionMetadata):
        print("Bot Started ✅")

    async def on_chat(self, user: User, message: str):
        msg = message.lower().split()
        if len(msg) == 0: return

        # 🌍 TELEPORT SYSTEM
        if msg[0] in self.public_floors:
            await self.highrise.teleport(user.id, self.public_floors[msg[0]])
            return

        # 🌟 VIP AREAS
        if msg[0] in self.vip_positions:
            if user.username in self.vips or user.username in self.admins:
                await self.highrise.teleport(user.id, self.vip_positions[msg[0]])
            else:
                await self.highrise.send_chat("❌ VIP only area")
            return

        # 👑 ADMIN COMMANDS (Kick, Ban, Mute, etc.)
        if user.username in self.admins:
            if msg[0] == "!kick" and len(msg) > 1:
                await self.highrise.kick_user(msg[1].replace("@",""))
            
            elif msg[0] == "!ban" and len(msg) > 1:
                await self.highrise.moderate_user(msg[1].replace("@",""), "ban", 3600)
            
            elif msg[0] == "!add" and len(msg) > 2:
                role, name = msg[1], msg[2].replace("@","")
                if role == "admin": self.admins.append(name)
                elif role == "vip": self.vips.append(name)
                await self.highrise.send_chat(f"✅ {name} added as {role}")

        # 🔐 OWNER ONLY
        if user.username == self.owner:
            if msg[0] == "!addemote" and len(msg) > 2:
                self.emotes[msg[2]] = msg[1]
                await self.highrise.send_chat(f"✅ Emote '{msg[2]}' added")

# 🚀 RUN BOT
if __name__ == "__main__":
    from highrise import BotRunner
    
    # Secrets se Token/ID uthana (Replit Settings mein TOKEN aur ROOM_ID banayein)
    room_id_code = os.environ.get('ROOM_ID', "69dbf0f3531fbf6ff18748e5")
    api_token_key = os.environ.get('TOKEN', "34f2f04114d5960cd18ef59fedd63ccb6572fd5658693a9d02cd9c9ce1e27799")

    keep_alive() # Server start
    
    bot = MyBot()
    BotRunner(bot, room_id=room_id_code, auth_token=api_token_key).run()
