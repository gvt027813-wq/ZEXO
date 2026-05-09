import asyncio, os, sys, re, random
from telethon import TelegramClient, functions, types, errors, events
from telethon.tl.types import KeyboardButtonCallback, ReplyInlineMarkup, KeyboardButtonRow

# --- CONFIGURATION ---
API_ID = 33205239
API_HASH = "d0e638a6c56bda91cd0ce4659d00a6b9"
BOT_TOKEN = "8555961488:AAHRYoBqJDgR-PfV0LeFRjJBvVNDBeEtpVU"
OWNER_ID = 8161593137
SESSION_DIR = './sessions'

if not os.path.exists(SESSION_DIR): os.makedirs(SESSION_DIR)

class ZexoV12Ultra:
    def __init__(self):
        self.bot = TelegramClient('bot_control', API_ID, API_HASH)
        self.workers = []
        self.waiting_for = {} 
        self.temp_clients = {} # OTP Login ke liye temp storage

    async def load_workers(self):
        self.workers = []
        files = [f for f in os.listdir(SESSION_DIR) if f.endswith('.session')]
        for f in files:
            if 'bot_control' in f: continue
            cl = TelegramClient(os.path.join(SESSION_DIR, f.replace('.session', '')), API_ID, API_HASH)
            try:
                await cl.connect()
                if await cl.is_user_authorized(): self.workers.append(cl)
            except: pass
        return len(self.workers)

    async def get_main_menu(self):
        return [
            [KeyboardButtonCallback("➕ ADD ID", b"act_add_id"), KeyboardButtonCallback("🔄 SYNC", b"sync")],
            [KeyboardButtonCallback("🛰️ JOIN/LEAVE", b"cat_join"), KeyboardButtonCallback("⚔️ RAID/SPAM", b"cat_raid")],
            [KeyboardButtonCallback("📈 BOOST/VIEW", b"cat_boost"), KeyboardButtonCallback("🛡️ REPORT/BAN", b"cat_report")],
            [KeyboardButtonCallback("🎭 STEALTH/BIO", b"cat_stealth"), KeyboardButtonCallback("🛑 EXIT", b"retire")]
        ]

    async def start(self):
        await self.bot.start(bot_token=BOT_TOKEN)
        await self.load_workers()
        print("✅ ZEXO V12 ULTRA: SYSTEM DEPLOYED")

        @self.bot.on(events.NewMessage(pattern='/start', from_users=OWNER_ID))
        async def start_handler(event):
            await event.reply(
                f"🔥 **ZEXO V12 ULTRA HUB**\n━━━━━━━━━━━━━━━━━━━━\n"
                f"🤖 **System:** Active\n🛰️ **Workers:** `{len(self.workers)}` IDs\n"
                f"⚡ **Delay:** `0.5s (Safe Mode)`\n━━━━━━━━━━━━━━━━━━━━",
                buttons=await self.get_main_menu()
            )

        @self.bot.on(events.CallbackQuery)
        async def callback_handler(event):
            if event.sender_id != OWNER_ID: return
            data = event.data

            # --- NAVIGATION ---
            if data == b"cat_join":
                btns = [[KeyboardButtonCallback("➕ Mass Join", b"act_join"), KeyboardButtonCallback("➖ Mass Leave", b"act_leave")], [KeyboardButtonCallback("🔙 Back", b"back")]]
                await event.edit("🛰️ **JOIN/LEAVE MENU**", buttons=btns)

            elif data == b"cat_raid":
                btns = [[KeyboardButtonCallback("🔥 Hyper Spam", b"act_spam"), KeyboardButtonCallback("📞 Raid VC", b"act_vraid")], [KeyboardButtonCallback("🔙 Back", b"back")]]
                await event.edit("⚔️ **RAID & DESTRUCTION**", buttons=btns)

            elif data == b"cat_boost":
                btns = [[KeyboardButtonCallback("👁️ Auto View", b"act_view"), KeyboardButtonCallback("❤️ Mass React", b"act_react")], [KeyboardButtonCallback("🔙 Back", b"back")]]
                await event.edit("📈 **ENGAGEMENT TOOLS**", buttons=btns)

            elif data == b"cat_report":
                btns = [[KeyboardButtonCallback("🛡️ Spam Report", b"act_report"), KeyboardButtonCallback("🔞 Adult Report", b"act_report_18")], [KeyboardButtonCallback("🔙 Back", b"back")]]
                await event.edit("🛡️ **TARGET REPORT HUB**", buttons=btns)

            # --- CORE ACTIONS ---
            elif data == b"act_add_id":
                self.waiting_for[OWNER_ID] = "get_phone"
                await event.reply("📲 **Enter Phone Number (with +91):**")

            elif data == b"act_view":
                self.waiting_for[OWNER_ID] = "view_link"
                await event.reply("🔗 **Send Channel/Post Link for Views:**")

            elif data == b"act_react":
                self.waiting_for[OWNER_ID] = "react_data"
                await event.reply("🎭 **Format: `link | emoji`**\nExample: `t.me/example/1 | 🔥`")

            elif data == b"act_report":
                self.waiting_for[OWNER_ID] = "report_target"
                await event.reply("🛡️ **Send Target @Username or Link to BAN:**")

            elif data == b"back":
                await event.edit("🚀 **MAIN CONTROL HUB**", buttons=await self.get_main_menu())

            elif data == b"sync":
                count = await self.load_workers()
                await event.answer(f"🔄 Synced! {count} Active.", alert=True)

            elif data == b"retire":
                await event.edit("🛑 **SHUTTING DOWN...**")
                sys.exit()

        # --- INPUT HANDLER (LOGIC) ---
        @self.bot.on(events.NewMessage(from_users=OWNER_ID))
        async def input_handler(event):
            if OWNER_ID not in self.waiting_for: return
            mode = self.waiting_for[OWNER_ID]
            text = event.raw_text

            # 1. ADD ID LOGIC
            if mode == "get_phone":
                phone = text.strip()
                new_cl = TelegramClient(f"{SESSION_DIR}/{phone}", API_ID, API_HASH)
                await new_cl.connect()
                try:
                    res = await new_cl.send_code_request(phone)
                    self.temp_clients[OWNER_ID] = (new_cl, phone, res.phone_code_hash)
                    self.waiting_for[OWNER_ID] = "get_otp"
                    await event.reply(f"📩 **OTP sent to {phone}. Send it here:**")
                except Exception as e: await event.reply(f"❌ Error: {e}")

            elif mode == "get_otp":
                otp = text.replace(" ", "")
                cl, phone, code_hash = self.temp_clients[OWNER_ID]
                try:
                    await cl.sign_in(phone, otp, phone_code_hash=code_hash)
                    await event.reply(f"✅ `{phone}` REQUEST COMPLETE")
                    self.workers.append(cl)
                except errors.SessionPasswordNeededError:
                    self.waiting_for[OWNER_ID] = "get_2fa"
                    await event.reply("🔐 **2FA Password Required. Send it:**")
                    return
                del self.waiting_for[OWNER_ID]

            # 2. AUTO VIEW & REACTION
            elif mode == "view_link":
                target = text.replace("https://t.me/", "").split('/')
                channel = target[0]
                await event.reply(f"👁️ **Boosting Views on {channel}...**")
                for cl in self.workers:
                    try:
                        await cl(functions.messages.GetMessagesViewsRequest(peer=channel, id=[int(target[1])], increment=True))
                        me = await cl.get_me()
                        await self.bot.send_message(OWNER_ID, f"👤 `+{me.phone}` ✅ VIEW DONE")
                    except: pass
                del self.waiting_for[OWNER_ID]

            elif mode == "react_data":
                try:
                    link, emoji = text.split('|')
                    parts = link.strip().replace("https://t.me/", "").split('/')
                    for cl in self.workers:
                        await cl(functions.messages.SendReactionRequest(peer=parts[0], msg_id=int(parts[1]), reaction=[types.ReactionEmoji(emoticon=emoji.strip())]))
                        me = await cl.get_me()
                        await self.bot.send_message(OWNER_ID, f"👤 `+{me.phone}` ✅ REACTION COMPLETE")
                except: await event.reply("❌ Format: `link | emoji`")
                del self.waiting_for[OWNER_ID]

            # 3. REPORT SYSTEM (FAST BAN)
            elif mode == "report_target":
                await event.reply(f"🛡️ **Launching Mass Report on `{text}`...**")
                for cl in self.workers:
                    try:
                        await cl(functions.account.ReportPeerRequest(peer=text, reason=types.InputReportReasonSpam(), message="Mass Spamming"))
                        me = await cl.get_me()
                        await self.bot.send_message(OWNER_ID, f"🛡️ `+{me.phone}` ✅ REPORT COMPLETE")
                        await asyncio.sleep(0.3) # Fast delay
                    except: pass
                await event.reply("🏁 **Reporting Task Finished.**")
                del self.waiting_for[OWNER_ID]

            # 4. RAID/SPAM (PURANI FEATURES)
            elif mode == "spam_data":
                target, msg = text.split('|')
                for _ in range(10): # Increased loops
                    tasks = [cl.send_message(target.strip(), msg.strip()) for cl in self.workers]
                    await asyncio.gather(*tasks, return_exceptions=True)
                    await asyncio.sleep(0.5)
                await event.reply("🔥 **RAID FINISHED.**")
                del self.waiting_for[OWNER_ID]

        await self.bot.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(ZexoV12Ultra().start())
