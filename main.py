import os
import asyncio
from flask import Flask
from threading import Thread
from highrise import BaseBot, Position
from highrise.models import SessionMetadata, User

# --- 🌐 24/7 SERVER SETUP (Flask) ---
app = Flask('')
@app.route('/')
def home():
    return "Bot is Online! ✅"

def run_server():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_server)
    t.daemon = True
    t.start()

# --- 🤖 HIGHRISE BOT CLASS ---
class MyBot(BaseBot):
    def __init__(self):
        super().__init__()
        # 👑 OWNER & ADMINS
        self.owner = "The_Corba_King" # Apna sahi username likhein
        self.admins = ["The_Corba_King"] 
        self.frozen_users = set()
        
        # 📍 TELEPORT POSITIONS
        self.public_floors = {
            "f1": Position(0, 0, 0),
            "f2": Position(0, 0, 0),
            "f3": Position(0, 0, 0)
        }

    async def on_start(self, session_metadata: SessionMetadata):
        print(f"✅ Bot is now Online in Highrise!")

    # --- ❄️ FREEZE PROTECTION ---
    async def on_user_move(self, user: User, pos: Position):
        if user.username in self.frozen_users:
            if isinstance(pos, Position):
                await self.highrise.teleport(user.id, Position(pos.x, pos.y, pos.z))

    async def on_chat(self, user: User, message: str):
        msg_lower = message.lower()

        # 🚀 TELEPORT (Sab ke liye)
        if msg_lower in self.public_floors:
            target_pos = self.public_floors[msg_lower]
            if target_pos.x != 0 or target_pos.y != 0:
                await self.highrise.teleport(user.id, target_pos)
            else:
                await self.highrise.send_chat(f"❌ {msg_lower} ki position set nahi hai.")
            return

        # 👑 ADMIN & MODERATION (Only for Admins)
        if user.username in self.admins:
            
            # --- SET TELEPORT ---
            if msg_lower.startswith("!set "):
                target = msg_lower.replace("!set ", "").strip()
                if target in self.public_floors:
                    room_users = await self.highrise.get_room_users()
                    for room_user, position in room_users.content:
                        if room_user.id == user.id:
                            self.public_floors[target] = position
                            await self.highrise.send_chat(f"📍 Location '{target}' set ho gayi hai! ✅")
                            break

            # --- FREEZE/UNFREEZE ---
            elif msg_lower.startswith("!freeze"):
                parts = message.split("@")
                if len(parts) > 1:
                    victim = parts[1].strip()
                    self.frozen_users.add(victim)
                    await self.highrise.send_chat(f"❄️ @{victim} ko freeze kar diya gaya!")

            elif msg_lower.startswith("!unfreeze"):
                parts = message.split("@")
                if len(parts) > 1:
                    victim = parts[1].strip()
                    self.frozen_users.discard(victim)
                    await self.highrise.send_chat(f"🔥 @{victim} ab hil sakta hai.")

            # --- BAN/UNBAN ---
            elif msg_lower.startswith("!ban"):
                parts = message.split("@")
                if len(parts) > 1:
                    victim = parts[1].strip()
                    await self.highrise.moderate_user(victim, "ban", 86400)
                    await self.highrise.send_chat(f"🔨 @{victim} ko BAN kar diya gaya!")

            elif msg_lower.startswith("!unban"):
                parts = message.split()
                if len(parts) > 1:
                    target_name = parts[1].replace("@", "").strip()
                    await self.highrise.moderate_user(target_name, "unban", 0)
                    await self.highrise.send_chat(f"🔓 @{target_name} ko unban kar diya!")

            # --- KICK ---
            elif msg_lower.startswith("!kick"):
                parts = message.split("@")
                if len(parts) > 1:
                    victim = parts[1].strip()
                    await self.highrise.kick_user(victim)
                    await self.highrise.send_chat(f"👞 @{victim} ko kick kar diya!")

            # --- ADD/REMOVE ADMIN ---
            elif msg_lower.startswith("!add admin"):
                parts = message.split("@")
                if len(parts) > 1:
                    new_admin = parts[1].strip()
                    if new_admin not in self.admins:
                        self.admins.append(new_admin)
                        await self.highrise.send_chat(f"🎊 Congratulations @{new_admin}! You are now an Admin! 👑")

            elif msg_lower.startswith("!remove admin"):
                parts = message.split("@")
                if len(parts) > 1:
                    target = parts[1].strip()
                    if target != self.owner:
                        self.admins.remove(target)
                        await self.highrise.send_chat(f"🚫 @{target} se admin powers le li gayi hain.")

# --- 🚀 RUNNER ---
if __name__ == "__main__":
    from highrise import BotRunner
    # Replit Secrets use karein ya direct value likhein
    room_id_code = os.environ.get('ROOM_ID', "69325fc85be7bfe87e2a172a")
    api_token_key = os.environ.get('TOKEN', "34f2f04114d5960cd18ef59fedd63ccb6572fd5658693a9d02cd9c9ce1e27799")

