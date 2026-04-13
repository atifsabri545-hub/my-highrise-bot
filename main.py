import os
import asyncio
from flask import Flask
from threading import Thread
from highrise import BaseBot, Position
from highrise.models import SessionMetadata, User

# --- 🌐 24/7 SERVER SETUP ---
app = Flask('')
@app.route('/')
def home(): return "Bot is Online! ✅"

def keep_alive():
    t = Thread(target=lambda: app.run(host='0.0.0.0', port=8080))
    t.daemon = True
    t.start()

# --- 🤖 HIGHRISE BOT CLASS ---
class MyBot(BaseBot):
    def __init__(self):
        super().__init__()
        self.owner = "The_Cobra_King"
        self.admins = ["The_Cobra_King"]
        self.frozen_users = {}  # Frozen users ki location save karne ke liye
        self.user_positions = {} # Sabki current position track karne ke liye
        
        # Teleport points
        self.public_floors = {
            "f1": Position(0, 0, 0),
            "f2": Position(0, 0, 0),
            "f3": Position(0, 0, 0)
        }

    async def on_start(self, session_metadata: SessionMetadata):
        print(f"✅ Bot Started for {self.owner}!")

    # --- ❄️ LIVE TRACKING & FREEZE LOGIC ---
    async def on_user_move(self, user: User, pos: Position):
        self.user_positions[user.username] = pos 
        
        # Agar user freeze hai toh usay wapis usi spot par teleport karo
        if user.username in self.frozen_users:
            frozen_pos = self.frozen_users[user.username]
            await self.highrise.teleport(user.id, frozen_pos)

    async def on_chat(self, user: User, message: str):
        msg = message.lower().strip()

        # 🚀 1. TELEPORT (Sab ke liye)
        if msg in self.public_floors:
            p = self.public_floors[msg]
            if p.x != 0 or p.y != 0:
                await self.highrise.teleport(user.id, p)
            return

        # 👑 2. ADMIN COMMANDS (Sirf Admins ke liye)
        if user.username in self.admins:
            
            # --- 📍 SET TELEPORT POSITION ---
            if msg.startswith("!set "):
                target = msg.replace("!set ", "").strip()
                if target in self.public_floors:
                    if user.username in self.user_positions:
                        self.public_floors[target] = self.user_positions[user.username]
                        await self.highrise.chat(f"📍 Location '{target}' saved successfully! ✅")
                    else:
                        await self.highrise.chat("⚠️ Aik baar hil kar dikhao taake bot position detect kar sake!")

            # --- ❄️ FREEZE COMMAND ---
            elif msg.startswith("!freeze"):
                parts = message.split("@")
                if len(parts) > 1:
                    victim = parts[1].strip()
                    if victim in self.user_positions:
                        self.frozen_users[victim] = self.user_positions[victim]
                        await self.highrise.chat(f"❄️ @{victim} ko freeze kar diya gaya! Hilna mana hai.")
                    else:
                        await self.highrise.chat(f"⚠️ @{victim} ki location nahi mil rahi.")

            # --- 🔥 UNFREEZE COMMAND ---
            elif msg.startswith("!unfreeze"):
                parts = message.split("@")
                if len(parts) > 1:
                    victim = parts[1].strip()
                    if victim in self.frozen_users:
                        del self.frozen_users[victim]
                        await self.highrise.chat(f"🔥 @{victim} ab aazad hai! Aap hil sakte hain.")
                    else:
                        await self.highrise.chat(f"❓ @{victim} frozen nahi hai.")

            # --- 👞 KICK COMMAND (Naya Fixed Tarika) ---
            elif msg.startswith("!kick"):
                parts = message.split("@")
                if len(parts) > 1:
                    victim = parts[1].strip()
                    try:
                        await self.highrise.moderate_user(victim, "kick")
                        await self.highrise.chat(f"👞 @{victim} ko nikaal diya gaya!")
                    except Exception as e:
                        print(f"Kick Error: {e}")

            # --- 🔨 BAN COMMAND ---
            elif msg.startswith("!ban"):
                parts = message.split("@")
                if len(parts) > 1:
                    victim = parts[1].strip()
                    await self.highrise.moderate_user(victim, "ban", 86400)
                    await self.highrise.chat(f"🔨 @{victim} ko BAN kar diya gaya!")

            # --- 🔓 UNBAN COMMAND ---
            elif msg.startswith("!unban"):
                parts = message.split()
                if len(parts) > 1:
                    name = parts[1].replace("@","").strip()
                    await self.highrise.moderate_user(name, "unban", 0)
                    await self.highrise.chat(f"🔓 @{name} ko unban kar diya gaya!")

            # --- 👑 ADD ADMIN ---
            elif msg.startswith("!add admin"):
                parts = message.split("@")
                if len(parts) > 1:
                    new_adm = parts[1].strip()
                    if new_adm not in self.admins:
                        self.admins.append(new_adm)
                        await self.highrise.chat(f"🎊 @{new_adm} is now Admin! 👑")

# --- 🚀 RUNNER ---
if __name__ == "__main__":
    from highrise import BotRunner
    # Replit Secrets ya Direct Values
    r_id = os.environ.get('ROOM_ID', "69325fc85be7bfe87e2a172a")
    token = os.environ.get('TOKEN', "b2989167e26d62f0fe26e2f35250f554ab507e5fddfd07ccc1130a3c4a120bf9")
    
    keep_alive() # Server start
    bot = MyBot()
    BotRunner(bot, room_id=r_id, auth_token=token).run()
