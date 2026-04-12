from highrise import BaseBot, Position
from highrise.models import SessionMetadata, User

class MyBot(BaseBot):

    # 🔐 OWNER (sirf tum)
    owner = "The_Cobra_King"

    # 👑 ROLES
    admins = ["The_Cobra_King"]
    vips = []

    # 🌍 PUBLIC FLOORS (sab ke liye)
    public_floors = {
        "f1": Position(0, 0, 0),
        "f2": Position(5, 0, 5),
        "f3": Position(10, 0, 10)
    }

    # 📍 CUSTOM POSITIONS
    vip_positions = {}
    admin_positions = {}

    # 🎭 EMOTES
    emotes = {}

    async def on_start(self, session_metadata: SessionMetadata):
        print("Bot Started ✅")

    async def on_chat(self, user: User, message: str):

        msg = message.lower().split()

        if len(msg) == 0:
            return

        # ---------------------------
        # 🌍 PUBLIC FLOORS (sab ke liye)
        # ---------------------------
        if msg[0] in self.public_floors:
            await self.teleport(user.id, self.public_floors[msg[0]])
            return

        # ---------------------------
        # 🌟 VIP POSITIONS
        # ---------------------------
        if msg[0] in self.vip_positions:
            if user.username in self.vips or user.username in self.admins:
                await self.teleport(user.id, self.vip_positions[msg[0]])
            else:
                await self.send_chat("❌ VIP only area")
            return

        # ---------------------------
        # 👑 ADMIN POSITIONS
        # ---------------------------
        if msg[0] in self.admin_positions:
            if user.username in self.admins:
                await self.teleport(user.id, self.admin_positions[msg[0]])
            else:
                await self.send_chat("❌ Admin only area")
            return

        # ---------------------------
        # 🎭 EMOTE USE
        # ---------------------------
        if msg[0] == "!emote" and len(msg) > 1:
            name = msg[1]
            if name in self.emotes:
                await self.send_emote(
                    emote_id=self.emotes[name],
                    user_id=user.id
                )
            else:
                await self.send_chat("❌ Emote not found")
            return

        # ---------------------------
        # 🚀 SUMMON (VIP + ADMIN)
        # ---------------------------
        if msg[0] == "!summon":
            if user.username in self.vips or user.username in self.admins:
                await self.teleport(user.id, Position(0, 0, 0))
                await self.send_chat(f"{user.username} summoned ✅")
            else:
                await self.send_chat("❌ VIP/Admin only")
            return

        # ---------------------------
        # 🔐 ADMIN ONLY COMMANDS
        # ---------------------------
        if user.username not in self.admins:
            return

        # 🔹 KICK
        if msg[0] == "!kick" and len(msg) > 1:
            await self.kick_user(msg[1].replace("@",""))

        # 🔹 BAN
        if msg[0] == "!ban" and len(msg) > 1:
            await self.ban_user(msg[1].replace("@",""))

        # 🔹 MUTE
        if msg[0] == "!mute" and len(msg) > 1:
            await self.mute_user(msg[1].replace("@",""), duration=300)

        # 🔹 UNMUTE
        if msg[0] == "!unmute" and len(msg) > 1:
            await self.unmute_user(msg[1].replace("@",""))

        # 🔹 FREEZE
        if msg[0] == "!freeze" and len(msg) > 1:
            await self.send_chat(f"{msg[1]} frozen 🧊")

        # ---------------------------
        # 👑 ROLE SYSTEM
        # ---------------------------
        if msg[0] == "!add" and len(msg) > 2:
            role = msg[1]
            username = msg[2].replace("@","")

            if role == "admin":
                if username not in self.admins:
                    self.admins.append(username)
                    await self.send_chat(f"✅ {username} is now Admin")

            elif role == "vip":
                if username not in self.vips:
                    self.vips.append(username)
                    await self.send_chat(f"🌟 {username} is now VIP")

        if msg[0] == "!radmin" and len(msg) > 1:
            u = msg[1].replace("@","")
            if u in self.admins:
                self.admins.remove(u)

        if msg[0] == "!rvip" and len(msg) > 1:
            u = msg[1].replace("@","")
            if u in self.vips:
                self.vips.remove(u)

        # ---------------------------
        # 📍 POSITION SYSTEM
        # ---------------------------
        if msg[0] == "!padd" and len(msg) > 2:
            role = msg[1]
            name = msg[2]

            if role == "vip":
                self.vip_positions[name] = Position(2,0,2)
                await self.send_chat(f"🌟 VIP place '{name}' added")

            elif role == "admin":
                self.admin_positions[name] = Position(8,0,8)
                await self.send_chat(f"👑 Admin place '{name}' added")

        if msg[0] == "!rpos" and len(msg) > 1:
            name = msg[1]
            if name in self.vip_positions:
                del self.vip_positions[name]
            if name in self.admin_positions:
                del self.admin_positions[name]
            await self.send_chat(f"❌ Position '{name}' removed")

        # ---------------------------
        # 🔐 OWNER ONLY (SUPER CONTROL 🔥)
        # ---------------------------
        if user.username != self.owner:
            return

        # 🎭 ADD EMOTE
        if msg[0] == "!addemote" and len(msg) > 2:
            code = msg[1]
            name = msg[2]
            self.emotes[name] = code
            await self.send_chat(f"✅ Emote '{name}' added")

        # 🎭 REMOVE EMOTE
        if msg[0] == "!rememote" and len(msg) > 1:
            name = msg[1]
            if name in self.emotes:
                del self.emotes[name]
                await self.send_chat(f"❌ Emote '{name}' removed")


# 🚀 RUN BOT
if __name__ == "__main__":
    from highrise import BotRunner

    bot = MyBot()

    BotRunner(
        bot,
        room_id="69dbcc35472c2d9ca26654cd",
        auth_token="50ffcb2b330efc2704eb35bc9ab6ab320bf790b3a78ec6a85a4af0aadf557318"
    ).run()
