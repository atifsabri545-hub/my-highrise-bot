import os
import asyncio
from flask import Flask
from threading import Thread
from highrise import BaseBot, Position
from highrise.models import SessionMetadata, User

# --- 🌐 24/7 SERVER ---
app = Flask('')
@app.route('/')
def home(): return "Bot is Online! ✅"

def keep_alive():
    t = Thread(target=lambda: app.run(host='0.0.0.0', port=8080))
    t.daemon = True
    t.start()

class MyBot(BaseBot):
    def __init__(self):
        super().__init__()
        self.owner = "The_Cobra_King"
        self.admins = ["The_Cobra_King"]
        self.frozen_users = {}
        self.user_positions = {} 
        
        self.public_floors = {
            "f1": Position(0, 0, 0),
            "f2": Position(0, 0, 0),
            "f3": Position(0, 0, 0)
        }

    async def on_start(self, session_metadata: SessionMetadata):
        print(f"✅ Bot Started! Owner: {self.owner}")

    async def on_user_move(self, user: User, pos: Position):
        self.user_positions[user.username] = pos 
        if user.username in self.frozen_users:
            await self.highrise.teleport(user.id, self.frozen_users[user.username])

    async def on_chat(self, user: User, message: str):
        msg = message.lower().strip()

        # 👑 ADMIN COMMANDS
        if user.username in self.admins:
            
            # --- 🔨 3600 DAYS BAN ---
            if msg.startswith("!ban"):
                parts = message.split("@")
                if len(parts) > 1:
                    victim = parts[1].strip()
                    try:
                        # 3600 days = 311040000 seconds
                        ban_seconds = 3600 * 24 * 60 * 60 
                        await self.highrise.moderate_user(victim, "ban", ban_seconds)
                        await self.highrise.chat(f"🔨 @{victim} ko 3600 dino ke liye BAN kar diya gaya!")
                    except Exception as e:
                        await self.highrise.chat(f"❌ Error: Bot ko moderator banayein!")

            # --- 🔓 UNBAN ---
            elif msg.startswith("!unban"):
                parts = message.split()
                if len(parts) > 1:
                    name = parts[1].replace("@","").strip()
                    try:
                        await self.highrise.moderate_user(name, "unban", 0)
                        await self.highrise.chat(f"🔓 @{name} Unbanned!")
                    except:
                        await self.highrise.chat(f"❌ Unban nahi ho saka.")

            # --- 👞 KICK (Sahi Command) ---
            elif msg.startswith("!kick"):
                parts = message.split("@")
                if len(parts) > 1:
                    victim = parts[1].strip()
                    try:
                        # Highrise mein kick ke liye ye command best hai
                        await self.highrise.moderate_user(victim, "kick")
                        await self.highrise.chat(f"👞 @{victim} ko kick kar diya!")
                    except:
                        # Agar kick kaam na kare toh 1 min ban (auto-kick)
                        try:
                            await self.highrise.moderate_user(victim, "ban", 60)
                            await self.highrise.chat(f"👞 @{victim} kicked via short-ban!")
                        except:
                            await self.highrise.chat(f"❌ Bot ke paas kick power nahi hai!")

            # --- ❄️ FREEZE / UNFREEZE ---
            elif msg.startswith("!freeze"):
                parts = message.split("@")
                if len(parts) > 1:
                    v = parts[1].strip()
                    if v in self.user_positions:
                        self.frozen_users[v] = self.user_positions[v]
                        await self.highrise.chat(f"❄️ @{v} Frozen!")

            elif msg.startswith("!unfreeze"):
                parts = message.split("@")
                if len(parts) > 1:
                    v = parts[1].strip()
                    self.frozen_users.pop(v, None)
                    await self.highrise.chat(f"🔥 @{v} Unfrozen!")

            # --- 📍 SET POSITION ---
            elif msg.startswith("!set "):
                target = msg.replace("!set ", "").strip()
                if target in self.public_floors and user.username in self.user_positions:
                    self.public_floors[target] = self.user_positions[user.username]
                    await self.highrise.chat(f"📍 '{target}' set ho gaya!")

# --- 🚀 RUNNER ---
if __name__ == "__main__":
    from highrise import BotRunner
    r_id = os.environ.get('ROOM_ID', "69325fc85be7bfe87e2a172a")
    token = os.environ.get('TOKEN', "6cc0e2364543d2936d20e17462459de77d61f7d30a817d38291cf202cb468e5b")
    keep_alive()
    BotRunner(MyBot(), room_id=r_id, auth_token=token).run()
