import os
import json
import asyncio
from flask import Flask
from threading import Thread
from highrise import BaseBot, Position
from highrise.models import SessionMetadata, User

# --- 🌐 SERVER SETUP (24/7) ---
app = Flask('')
@app.route('/')
def home(): return "Cobra King Bot is Online! ✅"

def keep_alive():
    t = Thread(target=lambda: app.run(host='0.0.0.0', port=8080))
    t.daemon = True
    t.start()

class MyBot(BaseBot):
    def __init__(self):
        super().__init__()
        self.owner = "The_Cobra_King"
        self.filename = "admins.json"
        self.loc_file = "locations.json"
        self.vip_file = "vips.json"
        
        # Permanent Data Load
        self.admins = self.load_data(self.filename, [self.owner])
        self.vips = self.load_data(self.vip_file, [])
        self.locations = self.load_data(self.loc_file, {"f1": None, "f2": None, "f3": None, "admin_area": None, "vip_area": None})
        
        self.user_positions = {}
        self.frozen_users = {}

    def load_data(self, file, default):
        if os.path.exists(file):
            try:
                with open(file, "r") as f:
                    data = json.load(f)
                    if file == self.loc_file:
                        for k, v in data.items():
                            if v: data[k] = Position(v['x'], v['y'], v['z'])
                    return data
            except: return default
        return default

    def save_data(self, file, data):
        with open(file, "w") as f:
            if file == self.loc_file:
                json_ready = {k: ({"x": v.x, "y": v.y, "z": v.z} if v else None) for k, v in data.items()}
                json.dump(json_ready, f)
            else:
                json.dump(data, f)

    async def on_start(self, session_metadata: SessionMetadata):
        print(f"✅ Bot Started! Master: {self.owner}")

    async def on_user_move(self, user: User, pos: Position):
        self.user_positions[user.username] = pos
        
        # ❄️ FREEZE CHECK
        if user.username in self.frozen_users:
            await self.highrise.teleport(user.id, self.frozen_users[user.username])
            return

        # 🛡️ GUARD SYSTEM (Whisper/DM Warning)
        if self.locations["admin_area"] and user.username not in self.admins:
            dist = ((pos.x - self.locations["admin_area"].x)**2 + (pos.z - self.locations["admin_area"].z)**2)**0.5
            if dist < 1.5:
                await self.highrise.send_whisper(user.id, f"@{user.username} you are not admin 🚫")

    async def on_chat(self, user: User, message: str):
        msg = message.lower().strip()

        # --- 🌍 PUBLIC COMMANDS (Sab ke liye) ---
        if msg in ["f1", "f2", "f3"]:
            target = self.locations.get(msg)
            if target: 
                await self.highrise.teleport(user.id, target)
            return

        # --- 👑 ADMIN & OWNER COMMANDS ---
        if user.username in self.admins:
            
            # 🔨 MODERATION (FIXED CRASH)
            if msg.startswith("!kick"):
                parts = message.split("@")
                if len(parts) > 1:
                    victim_name = parts[1].strip()
                    room_users = await self.highrise.get_room_users()
                    target = next((u for u, p in room_users.content if u.username.lower() == victim_name.lower()), None)
                    if target:
                        await self.highrise.kick_user(target.id)
                        await self.highrise.chat(f"👞 @{victim_name} ko kick kar diya!")

            elif msg.startswith("!mute"):
                parts = message.split("@")
                if len(parts) > 1:
                    victim_name = parts[1].strip()
                    room_users = await self.highrise.get_room_users()
                    target = next((u for u, p in room_users.content if u.username.lower() == victim_name.lower()), None)
                    if target:
                        await self.highrise.mute_user(target.id, 1800) # 30 mins
                        await self.highrise.chat(f"🔇 @{victim_name} muted for 30m")

            elif msg.startswith("!unmute"):
                parts = message.split("@")
                if len(parts) > 1:
                    victim_name = parts[1].strip()
                    room_users = await self.highrise.get_room_users()
                    target = next((u for u, p in room_users.content if u.username.lower() == victim_name.lower()), None)
                    if target:
                        await self.highrise.mute_user(target.id, 1)
                        await self.highrise.chat(f"🔊 @{victim_name} unmuted")

            # ❄️ FREEZE/UNFREEZE
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
                    self.frozen_users.pop(parts[1].strip(), None)
                    await self.highrise.chat(f"🔥 Unfrozen!")

            # 🚀 BRING
            elif msg.startswith("!bring"):
                parts = message.split("@")
                if len(parts) > 1:
                    target_name = parts[1].strip()
                    if user.username in self.user_positions:
                        room_users = await self.highrise.get_room_users()
                        target = next((u for u, p in room_users.content if u.username.lower() == target_name.lower()), None)
                        if target: await self.highrise.teleport(target.id, self.user_positions[user.username])

            # 📍 POSITION SETUP
            elif msg.startswith("!set "):
                loc = msg.replace("!set ", "").strip()
                curr = self.user_positions.get(user.username)
                if curr and loc in ["f1", "f2", "f3", "admin_area", "vip_area"]:
                    self.locations[loc] = curr
                    self.save_data(self.loc_file, self.locations)
                    await self.highrise.chat(f"📍 {loc} saved permanently!")

            # 👥 MANAGEMENT
            elif msg.startswith("!add admin"):
                parts = message.split("@")
                if len(parts) > 1:
                    new = parts[1].strip()
                    if new not in self.admins:
                        self.admins.append(new); self.save_data(self.filename, self.admins)
                        await self.highrise.chat(f"@{new} now have a admin power 👑")

            elif msg.startswith("!remove admin"):
                parts = message.split("@")
                if len(parts) > 1:
                    rem = parts[1].strip()
                    if rem in self.admins and rem != self.owner:
                        self.admins.remove(rem); self.save_data(self.filename, self.admins)
                        await self.highrise.chat(f"@{user.username} your removed @{rem} from admin")

            elif msg == "!adminlist":
                list_text = " , ".join([f"@{a}" for a in self.admins])
                await self.highrise.chat(f"👥 Admins: {list_text}")

# --- 🚀 RUNNER ---
if __name__ == "__main__":
    from highrise import BotRunner
    r_id = os.environ.get('ROOM_ID', "69325fc85be7bfe87e2a172a")
    token = os.environ.get('TOKEN', "d9f7a9c578547dbb980205d499232009a1df4e06163059871194df5a6c70fbcb")
    keep_alive()
    BotRunner(MyBot(), room_id=r_id, auth_token=token).run()
