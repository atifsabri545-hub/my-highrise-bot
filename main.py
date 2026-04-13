import os
import json
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
        self.filename = "admins.json"
        self.loc_file = "locations.json"
        
        # Load Data
        self.admins = self.load_data(self.filename, [self.owner])
        self.locations = self.load_data(self.loc_file, {"f1": None, "f2": None, "f3": None, "admin_area": None, "vip_area": None})
        
        self.user_positions = {}

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

    async def on_user_move(self, user: User, pos: Position):
        self.user_positions[user.username] = pos
        # Guard System (Whisper Warning)
        if self.locations["admin_area"] and user.username not in self.admins:
            dist = ((pos.x - self.locations["admin_area"].x)**2 + (pos.z - self.locations["admin_area"].z)**2)**0.5
            if dist < 1.5:
                await self.highrise.send_whisper(user.id, f"@{user.username} you are not admin 🚫")

    async def on_chat(self, user: User, message: str):
        msg = message.lower().strip()

        # --- 🌍 PUBLIC COMMANDS (Sab ke liye) ---
        if msg in ["f1", "f2", "f3"]:
            target_pos = self.locations.get(msg)
            if target_pos:
                await self.highrise.teleport(user.id, target_pos)
            else:
                await self.highrise.chat(f"⚠️ {msg} abhi set nahi kiya gaya.")

        # --- 👑 ADMIN & OWNER COMMANDS ---
        if user.username in self.admins:
            
            # Position Set Karna (Sirf Admin kar sakta hai)
            if msg.startswith("!set "):
                target = msg.replace("!set ", "").strip()
                current_pos = self.user_positions.get(user.username)
                
                if current_pos:
                    if target in ["f1", "f2", "f3"]:
                        self.locations[target] = current_pos
                        self.save_data(self.loc_file, self.locations)
                        await self.highrise.chat(f"📍 Location {target} set permanently! Ab aam log use kar sakte hain.")
                    
                    elif target == "admin":
                        self.locations["admin_area"] = current_pos
                        self.save_data(self.loc_file, self.locations)
                        await self.highrise.chat("🛡️ Admin Guard Zone set!")

            # Admin Management
            elif msg.startswith("!add admin"):
                parts = message.split("@")
                if len(parts) > 1:
                    new_adm = parts[1].strip()
                    if new_adm not in self.admins:
                        self.admins.append(new_adm); self.save_data(self.filename, self.admins)
                        await self.highrise.chat(f"@{new_adm} now have a admin power 👑")

# --- 🚀 RUNNER ---
if __name__ == "__main__":
    from highrise import BotRunner
    r_id = os.environ.get('ROOM_ID', "69325fc85be7bfe87e2a172a")
    token = os.environ.get('TOKEN', "80d216c3cd49a3f1518e282ba6f2f3b9d03fd1c5a9852b93c5795c42023cca41")
    keep_alive()
    BotRunner(MyBot(), room_id=r_id, auth_token=token).run()
