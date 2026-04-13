import os
import asyncio
from flask import Flask
from threading import Thread
from highrise import BaseBot, Position
from highrise.models import SessionMetadata, User

# --- 🌐 SERVER ---
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
        self.frozen_users = set()
        self.user_positions = {} 
        
        self.public_floors = {
            "f1": Position(0, 0, 0),
            "f2": Position(0, 0, 0),
            "f3": Position(0, 0, 0)
        }

    async def on_start(self, session_metadata: SessionMetadata):
        print(f"✅ Bot Started for {self.owner}")

    async def on_user_move(self, user: User, pos: Position):
        self.user_positions[user.username] = pos 
        if user.username in self.frozen_users:
            # Agar frozen hai toh wapis usi purani jagah phenk do
            await self.highrise.teleport(user.id, pos)

    async def on_chat(self, user: User, message: str):
        msg = message.lower()

        # 🚀 TELEPORT
        if msg in self.public_floors:
            p = self.public_floors[msg]
            if p.x != 0 or p.y != 0:
                await self.highrise.teleport(user.id, p)
            return

        # 👑 ADMIN COMMANDS
        if user.username in self.admins:
            
            # --- SAFE SET POSITION ---
            if msg.startswith("!set "):
                target = msg.replace("!set ", "").strip()
                if target in self.public_floors:
                    if user.username in self.user_positions:
                        self.public_floors[target] = self.user_positions[user.username]
                        # Fix: send_chat ki jagah self.highrise.chat use kiya
                        await self.highrise.chat(f"📍 Location '{target}' saved successfully! ✅")
                    else:
                        await self.highrise.chat("⚠️ Ek baar hil kar dikhao taake bot position detect kar sake!")

            # --- FREEZE/UNFREEZE ---
            elif msg.startswith("!freeze"):
                p = message.split("@")
                if len(p) > 1:
                    victim = p[1].strip()
                    self.frozen_users.add(victim)
                    await self.highrise.chat(f"❄️ @{victim} Frozen!")

            elif msg.startswith("!unfreeze"):
                p = message.split("@")
                if len(p) > 1:
                    victim = p[1].strip()
                    self.frozen_users.discard(victim)
                    await self.highrise.chat(f"🔥 @{victim} Unfrozen!")

            # --- BAN/UNBAN/KICK ---
            elif msg.startswith("!ban"):
                p = message.split("@")
                if len(p) > 1:
                    await self.highrise.moderate_user(p[1].strip(), "ban", 86400)
                    await self.highrise.chat(f"🔨 @{p[1].strip()} Banned!")
            
            elif msg.startswith("!unban"):
                p = message.split()
                if len(p) > 1:
                    name = p[1].replace("@","")
                    await self.highrise.moderate_user(name, "unban", 0)
                    await self.highrise.chat(f"🔓 @{name} Unbanned!")

            elif msg.startswith("!kick"):
                p = message.split("@")
                if len(p) > 1:
                    await self.highrise.kick_user(p[1].strip())
                    await self.highrise.chat(f"👞 @{p[1].strip()} Kicked!")

            # --- ADMIN ADD ---
            elif msg.startswith("!add admin"):
                p = message.split("@")
                if len(p) > 1:
                    new_adm = p[1].strip()
                    if new_adm not in self.admins:
                        self.admins.append(new_adm)
                        await self.highrise.chat(f"🎊 @{new_adm} is now Admin! 👑")

# --- 🚀 RUN ---
if __name__ == "__main__":
    from highrise import BotRunner
    r_id = os.environ.get('ROOM_ID', "69325fc85be7bfe87e2a172a")
    token = os.environ.get('TOKEN', "b2989167e26d62f0fe26e2f35250f554ab507e5fddfd07ccc1130a3c4a120bf9")
    keep_alive()
    BotRunner(MyBot(), room_id=r_id, auth_token=token).run()
