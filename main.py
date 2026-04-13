import os, json, asyncio
from flask import Flask
from threading import Thread
from highrise import BaseBot, Position
from highrise.models import SessionMetadata, User

# --- 🌐 SERVER (24/7) ---
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
        
        # Load Permanent Data
        self.admins = self.load_data(self.filename, [self.owner])
        self.locations = self.load_data(self.loc_file, {"f1": None, "f2": None, "f3": None, "admin_area": None})
        
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
        self.user_positions[user.id] = (user.username, pos)
        
        if user.username in self.frozen_users:
            await self.highrise.teleport(user.id, self.frozen_users[user.username])
            return

        if self.locations["admin_area"] and user.username not in self.admins:
            a_pos = self.locations["admin_area"]
            dist = ((pos.x - a_pos.x)**2 + (pos.z - a_pos.z)**2)**0.5
            if dist < 1.5:
                await self.highrise.send_whisper(user.id, f"@{user.username} you are not admin 🚫")

    async def on_chat(self, user: User, message: str):
        msg = message.lower().strip()

        # --- 🌍 PUBLIC ---
        if msg in ["f1", "f2", "f3"]:
            target = self.locations.get(msg)
            if target: await self.highrise.teleport(user.id, target)
            return

        # --- 👑 ADMIN ONLY ---
        if user.username in self.admins:
            try:
                # 🔨 MODERATION
                if msg.startswith("!kick"):
                    target_user = msg.split("@")[-1].strip()
                    room_users = await self.highrise.get_room_users()
                    for u, p in room_users.content:
                        if u.username.lower() == target_user.lower():
                            await self.highrise.kick_user(u.id)
                            await self.highrise.chat(f"👞 @{u.username} kicked!")
                            break

                elif msg.startswith("!mute"):
                    target_user = msg.split("@")[-1].strip()
                    room_users = await self.highrise.get_room_users()
                    for u, p in room_users.content:
                        if u.username.lower() == target_user.lower():
                            await self.highrise.mute_user(u.id, 1800)
                            await self.highrise.chat(f"🔇 @{u.username} muted 30m")
                            break

                # ❄️ FREEZE
                elif msg.startswith("!freeze"):
                    target_user = msg.split("@")[-1].strip()
                    for uid, (uname, upos) in self.user_positions.items():
                        if uname.lower() == target_user.lower():
                            self.frozen_users[uname] = upos
                            await self.highrise.chat(f"❄️ @{uname} Frozen!")
                            break

                elif msg.startswith("!unfreeze"):
                    target_user = msg.split("@")[-1].strip()
                    self.frozen_users.pop(target_user, None)
                    await self.highrise.chat(f"🔥 Unfrozen!")

                # 🚀 BRING
                elif msg.startswith("!bring"):
                    target_user = msg.split("@")[-1].strip()
                    admin_pos = None
                    for uid, (uname, upos) in self.user_positions.items():
                        if uname == user.username: admin_pos = upos
                    
                    if admin_pos:
                        room_users = await self.highrise.get_room_users()
                        for u, p in room_users.content:
                            if u.username.lower() == target_user.lower():
                                await self.highrise.teleport(u.id, admin_pos)
                                break

                # 📍 POSITION SETTING
                elif msg.startswith("!set "):
                    loc_name = msg.replace("!set ", "").strip()
                    admin_pos = None
                    for uid, (uname, upos) in self.user_positions.items():
                        if uname == user.username: admin_pos = upos
                    
                    if admin_pos and loc_name in ["f1", "f2", "f3", "admin_area"]:
                        self.locations[loc_name] = admin_pos
                        self.save_data(self.loc_file, self.locations)
                        await self.highrise.chat(f"📍 {loc_name} Saved!")

                # 👥 MANAGEMENT
                elif msg.startswith("!add admin"):
                    new = msg.split("@")[-1].strip()
                    if new not in self.admins:
                        self.admins.append(new); self.save_data(self.filename, self.admins)
                        await self.highrise.chat(f"@{new} now have a admin power 👑")

                elif msg.startswith("!remove admin"):
                    rem = msg.split("@")[-1].strip()
                    if rem in self.admins and rem != self.owner:
                        self.admins.remove(rem); self.save_data(self.filename, self.admins)
                        await self.highrise.chat(f"🚫 Removed @{rem}")

                elif msg == "!adminlist":
                    await self.highrise.chat(f"👥 Admins: {', '.join(['@'+a for a in self.admins])}")

            except Exception as e:
                print(f"Error: {e}")

# --- 🚀 RUN ---
if __name__ == "__main__":
    from highrise import BotRunner
    r_id = os.environ.get('ROOM_ID', "69325fc85be7bfe87e2a172a")
    token = os.environ.get('TOKEN', "d9f7a9c578547dbb980205d499232009a1df4e06163059871194df5a6c70fbcb")
    keep_alive()
    BotRunner(MyBot(), room_id=r_id, auth_token=token).run()
