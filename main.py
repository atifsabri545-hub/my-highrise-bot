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
        print(f"✅ Bot Started for {self.owner}!")

    async def on_user_move(self, user: User, pos: Position):
        self.user_positions[user.username] = pos 
        if user.username in self.frozen_users:
            await self.highrise.teleport(user.id, self.frozen_users[user.username])

    async def on_chat(self, user: User, message: str):
        msg = message.lower().strip()

        # 👑 ADMIN COMMANDS ONLY
        if user.username in self.admins:
            
            # --- 🔨 BAN COMMAND (3600 DAYS) ---
            if msg.startswith("!ban"):
                parts = message.split("@")
                if len(parts) > 1:
                    victim = parts[1].strip()
                    try:
                        # 3600 days in seconds = 311,040,000
                        ban_time = 3600 * 24 * 60 * 60 
                        await self.highrise.moderate_user(victim, "ban", ban_time)
                        await self.highrise.chat(f"🔨 @{victim} ko 3600 dino ke liye BAN kar diya gaya! Bye bye.")
                    except Exception as e:
                        await self.highrise.chat(f"❌ Ban fail: Bot ke paas permissions nahi hain.")
                        print(f"Ban Error: {e}")

            # --- 🔓 UNBAN COMMAND (FIXED) ---
            elif msg.startswith("!unban"):
                # Format: !unban username (bina @ ke bhi kaam karega)
                parts = message.split()
                if len(parts) > 1:
                    target_name = parts[1].replace("@", "").strip()
                    try:
                        await self.highrise.moderate_user(target_name, "unban", 0)
                        await self.highrise.chat(f"🔓 @{target_name} ko unban kar diya gaya hai. Wo ab wapis aa sakta hai.")
                    except Exception as e:
                        await self.highrise.chat(f"❌ Unban fail: Username check karein.")
                        print(f"Unban Error: {e}")

            # --- 👞 KICK COMMAND ---
            elif msg.startswith("!kick"):
                parts = message.split("@")
                if len(parts) > 1:
                    victim = parts[1].strip()
                    try:
                        await self.highrise.moderate_user(victim, "kick")
                        await self.highrise.chat(f"👞 @{victim} Kicked!")
                    except Exception as e:
                        print(f"Kick Error: {e}")

            # --- ❄️ FREEZE / UNFREEZE ---
            elif msg.startswith("!freeze"):
                parts = message.split("@")
                if len(parts) > 1:
                    victim = parts[1].strip()
                    if victim in self.user_positions:
                        self.frozen_users[victim] = self.user_positions[victim]
                        await self.highrise.chat(f"❄️ @{victim} Frozen!")

            elif msg.startswith("!unfreeze"):
                parts = message.split("@")
                if len(parts) > 1:
                    victim = parts[1].strip()
                    if victim in self.frozen_users:
                        del self.frozen_users[victim]
                        await self.highrise.chat(f"🔥 @{victim} Unfrozen!")

            # --- 📍 SET TELEPORT ---
            elif msg.startswith("!set "):
                target = msg.replace("!set ", "").strip()
                if target in self.public_floors:
                    if user.username in self.user_positions:
                        self.public_floors[target] = self.user_positions[user.username]
                        await self.highrise.chat(f"📍 '{target}' set successfully!")

# --- 🚀 RUNNER ---
if __name__ == "__main__":
    from highrise import BotRunner
    r_id = os.environ.get('ROOM_ID', "69325fc85be7bfe87e2a172a")
    token = os.environ.get('TOKEN', "6cc0e2364543d2936d20e17462459de77d61f7d30a817d38291cf202cb468e5b")
    keep_alive()
    BotRunner(MyBot(), room_id=r_id, auth_token=token).run()
