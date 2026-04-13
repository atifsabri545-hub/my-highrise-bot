import os
import json
import asyncio
from flask import Flask
from threading import Thread
from highrise import BaseBot, Position
from highrise.models import SessionMetadata, User

# --- 🌐 SERVER SETUP ---
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
        self.user_positions = {}
        self.filename = "admins.json"
        self.admins = self.load_admins()

    # --- 📂 DATA SAVING ---
    def load_admins(self):
        if os.path.exists(self.filename):
            with open(self.filename, "r") as f:
                return json.load(f)
        return [self.owner]

    def save_admins(self):
        with open(self.filename, "w") as f:
            json.dump(self.admins, f)

    async def on_start(self, session_metadata: SessionMetadata):
        print(f"✅ Bot Started! Total Admins: {len(self.admins)}")

    async def on_user_move(self, user: User, pos: Position):
        # Har bande ki location track karna zaroori hai bring command ke liye
        self.user_positions[user.username] = pos

    async def on_chat(self, user: User, message: str):
        msg = message.lower().strip()

        # --- 👑 ADMIN & OWNER COMMANDS ---
        if user.username in self.admins:

            # 1. BRING COMMAND (Logo ko apne paas bulana)
            if msg.startswith("!bring"):
                parts = message.split("@")
                if len(parts) > 1:
                    target_user = parts[1].strip()
                    
                    # Check karo ke kya Admin (Aap) ki position bot ke paas hai?
                    if user.username in self.user_positions:
                        admin_pos = self.user_positions[user.username]
                        
                        # Room ke saare users ki list check karo
                        room_users = await self.highrise.get_room_users()
                        target_id = None
                        
                        for u, pos in room_users.content:
                            if u.username.lower() == target_user.lower():
                                target_id = u.id
                                break
                        
                        if target_id:
                            await self.highrise.teleport(target_id, admin_pos)
                            await self.highrise.chat(f"🚀 @{target_user} ko @{user.username} ke paas bulaya gaya hai!")
                        else:
                            await self.highrise.chat(f"❌ @{target_user} room mein nahi mila.")
                    else:
                        await self.highrise.chat("⚠️ Aik qadam chalo taake bot aapki jagah dekh sake!")

            # 2. ADD ADMIN
            elif msg.startswith("!add admin"):
                parts = message.split("@")
                if len(parts) > 1:
                    new_admin = parts[1].strip()
                    if new_admin not in self.admins:
                        self.admins.append(new_admin)
                        self.save_admins()
                        await self.highrise.chat(f"@{new_admin} now have a admin power 👑")

            # 3. REMOVE ADMIN
            elif msg.startswith("!remove admin"):
                parts = message.split("@")
                if len(parts) > 1:
                    target = parts[1].strip()
                    if target != self.owner and target in self.admins:
                        self.admins.remove(target)
                        self.save_admins()
                        await self.highrise.chat(f"@{user.username} your removed @{target} from admin")

            # 4. ADMIN LIST
            elif msg == "!adminlist":
                list_text = " , ".join([f"@{a}" for a in self.admins])
                await self.highrise.chat(f"👥 Current Admins: {list_text}")

# --- 🚀 RUNNER ---
if __name__ == "__main__":
    from highrise import BotRunner
    r_id = os.environ.get('ROOM_ID', "69325fc85be7bfe87e2a172a")
    token = os.environ.get('TOKEN', "3db1a58ba9c8125cf6980e6bbac5a96d18f2feca83c54660ced82c7866aab8ac")
    keep_alive()
    BotRunner(MyBot(), room_id=r_id, auth_token=token).run()
