import time
import os
import json
import hashlib
import random
import math
from collections import Counter
from datetime import date, datetime, timedelta
import telebot
from telebot.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "8364074399:AAFqlIceG3pfTFw7qWiihwpb2CBFCD67vJM
ADMIN_IDS = [8131188115]

DATA_FILE = "data_xu.json"
HISTORY_FILE = "lich_su.json"
CHECKIN_FILE = "checkin.json"
VIP_FILE = "vip_users.json"

bot = telebot.TeleBot(TOKEN, parse_mode="Markdown")

# ================= FILE =================
def load_json(file):
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

user_data = load_json(DATA_FILE)
history_data = load_json(HISTORY_FILE)
checkin_data = load_json(CHECKIN_FILE)
vip_users = load_json(VIP_FILE)

tool_users = set()
admin_waiting = {}
pending_codes = {}
prediction_history = {}
pending_predictions = {}

# ================= VIP CHECK =================
def is_vip(uid):
    if uid not in vip_users:
        return False

    expire = vip_users[uid]

    if expire == "forever":
        return True

    today = datetime.now().strftime("%Y-%m-%d")
    if today > expire:
        vip_users.pop(uid)
        save_json(VIP_FILE, vip_users)
        return False

    return True

# ================= KEYBOARD =================
def main_keyboard(uid=None):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("🚀 BẮT ĐẦU TOOL SIÊU CẤP", "💎 GIÁ XU SIÊU HỜI")
    kb.row("👑 BẢNG XẾP HẠNG VIP", "🎁 NHẬN QUÀ MỖI NGÀY")
    kb.row("📊 TỔNG KẾT", "💰 NẠP TIỀN")
    kb.row("📞 ADMIN HỖ TRỢ", "🌍 THAM GIA CỘNG ĐỒNG")
    kb.row("📜 HƯỚNG DẪN TOOL", "📜 LỊCH SỬ")

    if uid and int(uid) in ADMIN_IDS:
        kb.row("🛠 ADMIN PANEL")

    return kb

# ================= START =================
@bot.message_handler(commands=["start"])
def start(message):
    uid = str(message.from_user.id)
    username = message.from_user.username or "Ẩn danh"

    user_data.setdefault(uid, {"xu": 10, "username": username})
    user_data[uid]["username"] = username
    save_json(DATA_FILE, user_data)

    bot.send_message(
        message.chat.id,
        f"✨ *CHÀO MỪNG ĐẾN TOOL SIÊU CẤP* ✨\n\n"
        f"👤 @{username}\n"
        f"💰 Số xu hiện tại: *{user_data[uid]['xu']}*",
        reply_markup=main_keyboard(uid)
    )

# ================= ADMIN PANEL =================
@bot.message_handler(func=lambda m: m.text == "🛠 ADMIN PANEL")
def admin_panel(message):
    if message.from_user.id not in ADMIN_IDS:
        return bot.reply_to(message, "❌ Bạn không có quyền.")

    bot.send_message(
        message.chat.id,
        "🛠 *ADMIN PANEL*\n\n"
        "🔥 /adduser <id> <ngày>\n"
        "🌟 /themuser <id>\n"
        "☠️ /removeuser <id>\n"
        "📁 /listusers\n"
        "📢 /broadcast <nội dung>"
    )

# ================= MENU =================
@bot.message_handler(func=lambda m: m.text == "🚀 BẮT ĐẦU TOOL SIÊU CẤP")
def start_tool(message):
    tool_users.add(str(message.from_user.id))
    bot.reply_to(message,
        "🔥 *TOOL ĐÃ KÍCH HOẠT*\n\n"
        "📥 Gửi MD5 (32 ký tự) để phân tích.\n"
        "⚡ Mỗi lần sử dụng trừ 1 xu."
    )

@bot.message_handler(func=lambda m: m.text == "📊 TỔNG KẾT")
def summary(message):
    uid = str(message.from_user.id)
    history = prediction_history.get(uid, [])

    if not history:
        return bot.reply_to(message, "❌ Chưa có dữ liệu.")

    total = len(history)
    correct = sum(1 for h in history if h["correct"])
    wrong = total - correct
    accuracy = round(correct / total * 100, 2)

    bot.reply_to(message,
        f"📊 TỔNG KẾT 30 VÁN GẦN NHẤT\n\n"
        f"🎯 Đúng: {correct}\n"
        f"❌ Sai: {wrong}\n"
        f"📈 Tỷ lệ chính xác: {accuracy}%"
    )
    
@bot.message_handler(func=lambda m: m.text == "💎 GIÁ XU SIÊU HỜI")
def price(message):
    bot.reply_to(message,
        "💎 *BẢNG GIÁ XU*\n\n"
"10 xu = 10.000đ\n"
        "50 xu = 45.000đ\n"
        "100 xu = 80.000đ\n\n"
        "📞 Liên hệ: https://t.me/HLong2002"
    )

@bot.message_handler(func=lambda m: m.text == "🎁 NHẬN QUÀ MỖI NGÀY")
def checkin(message):
    uid = str(message.from_user.id)
    today = str(date.today())

    if checkin_data.get(uid) == today:
        return bot.reply_to(message, "❌ Hôm nay bạn đã nhận rồi.")

    user_data.setdefault(uid, {"xu": 0, "username": message.from_user.username or "Ẩn danh"})
    user_data[uid]["xu"] += 5
    checkin_data[uid] = today

    save_json(DATA_FILE, user_data)
    save_json(CHECKIN_FILE, checkin_data)

    bot.reply_to(message, "🎉 Bạn nhận được *+5 xu*!")
    
@bot.message_handler(func=lambda m: m.text == "👑 BẢNG XẾP HẠNG VIP")
def ranking(message):
    top = sorted(user_data.items(), key=lambda x: x[1]["xu"], reverse=True)[:5]
    text = "👑 *TOP VIP*\n\n"
    for i, (uid, data) in enumerate(top, 1):
        text += f"{i}. @{data['username']} - {data['xu']} xu\n"
    bot.reply_to(message, text)

@bot.message_handler(func=lambda m: m.text == "📞 ADMIN HỖ TRỢ")
def admin_support(message):
    bot.reply_to(message, "📞 https://t.me/HLong2002")

@bot.message_handler(func=lambda m: m.text == "🌍 THAM GIA CỘNG ĐỒNG")
def community(message):
    bot.reply_to(message, "🌍 https://t.me/kiemlaimoingay68gb")

@bot.message_handler(func=lambda m: m.text == "📜 HƯỚNG DẪN TOOL")
def guide(message):
    bot.reply_to(message,
        "📜 *HƯỚNG DẪN*\n\n"
        "1️⃣ Bấm 🚀 BẮT ĐẦU TOOL\n"
        "2️⃣ Gửi MD5\n"
        "3️⃣ Nhận kết quả\n"
        "⚡ Mỗi lần trừ 1 xu"
    )

@bot.message_handler(func=lambda m: m.text == "📜 LỊCH SỬ")
def history(message):
    uid = str(message.from_user.id)
    if uid not in history_data:
        return bot.reply_to(message, "❌ Chưa có lịch sử nạp.")
    text = "📜 *LỊCH SỬ NẠP*\n\n"
    for item in history_data[uid][-5:]:
        text += f"{item['amount']}đ → {item['xu']} xu\n"
    bot.reply_to(message, text)

# ================= MD5 =================
@bot.message_handler(func=lambda m: m.text and len(m.text) == 32)
def md5_handler(message):
    uid = str(message.from_user.id)

    if uid not in tool_users:
        return

    if uid not in user_data:
        return

    if user_data[uid]["xu"] <= 0:
        return bot.reply_to(message, "❌ Bạn không đủ xu.")

    md5_input = message.text.strip().lower()

    try:
        int(md5_input, 16)
    except:
        return bot.reply_to(message, "❌ MD5 không hợp lệ.")

    counter = Counter(md5_input)

    # ===== Entropy =====
    entropy = 0
    for c in counter.values():
        p = c / 32
        entropy -= p * math.log2(p)

    entropy_score = (entropy - 3.75) * 0.5

    # ===== Bit balance =====
    binary = bin(int(md5_input, 16))[2:].zfill(128)
    ones = binary.count("1")
    zeros = 128 - ones

    bit_balance = ((ones - zeros) / 128) * 2

    # ===== Block analysis =====
    blocks = [md5_input[i:i+8] for i in range(0, 32, 8)]
    block_values = [int(b, 16) / 0xffffffff for b in blocks]

    mean_block = sum(block_values) / 4

    variance = sum((x - mean_block) ** 2 for x in block_values) / 4

    block_deviation = (mean_block - 0.5) * 2

    # ===== Repeat bias =====
    max_repeat = max(counter.values())
    repeat_bias = (max_repeat - 2) / 20

    # ===== Score tổng =====
    score = (
        entropy_score * 0.25 +
        bit_balance * 0.25 +
        block_deviation * 0.25 +
        variance * 0.15 +
        repeat_bias * 0.10
    )

    # ===== Winrate adjust =====
    history = prediction_history.get(uid, [])
    recent = history[-25:]

    if recent:
        wins = sum(1 for h in recent if h["correct"])
        winrate = wins / len(recent)

        score += (0.55 - winrate) * 0.05

    # ===== VIP bonus =====
    if is_vip(uid):
        score += 0.02

    # ===== Clamp score =====
    score = max(-0.25, min(0.25, score))

    # ===== Result =====
    result = "TÀI" if score > 0 else "XỈU"

    tai_percent = max(5, min(95, 50 + score * 100))
    xiu_percent = 100 - tai_percent
confidence = min(100, abs(score) * 300)

    pending_predictions[uid] = result

    # ===== Trừ xu =====
    user_data[uid]["xu"] -= 1
    save_json(DATA_FILE, user_data)

    # ===== Button xác nhận =====
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("🔥 KẾT QUẢ TÀI", callback_data="real_TÀI"),
        InlineKeyboardButton("💎 KẾT QUẢ XỈU", callback_data="real_XỈU")
    )

    bot.reply_to(
        message,
        f"🎰 DỰ ĐOÁN: 🔥 {result} 🔥\n"
        f"📊 Tài: {round(tai_percent,2)}% | Xỉu: {round(xiu_percent,2)}%\n"
        f"🎯 Độ tin cậy: {round(confidence,2)}%\n\n"
        f"💰 Xu còn lại: {user_data[uid]['xu']}",
        reply_markup=markup
    )
# ================= XÁC NHẬN =================
@bot.callback_query_handler(func=lambda c: c.data.startswith("real_"))
def confirm_real_result(call):
    uid = str(call.from_user.id)

    if uid not in pending_predictions:
        return

    predicted = pending_predictions.pop(uid)
    actual = call.data.split("_")[1]
    correct = predicted == actual

    prediction_history.setdefault(uid, [])
    prediction_history[uid].append({
        "predicted": predicted,
        "actual": actual,
        "correct": correct
    })

    prediction_history[uid] = prediction_history[uid][-30:]

    status = "✅ ĐÚNG" if correct else "❌ SAI"

    bot.answer_callback_query(call.id, status)
    bot.send_message(call.message.chat.id,
        f"📌 Kết quả thực tế: {actual}\n"
        f"🤖 Bot dự đoán: {predicted}\n"
        f"🎯 {status}"
    )
    # ================= NẠP TIỀN =================
@bot.message_handler(func=lambda m: m.text == "💰 NẠP TIỀN")
def deposit(message):
    uid = str(message.from_user.id)
    code = "NAP" + str(random.randint(10000, 99999))
    pending_codes[uid] = code

    qr = f"https://img.vietqr.io/image/MB-0848794679-compact2.png?addInfo={code}"

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("✅ ĐÃ CHUYỂN KHOẢN", callback_data="confirm"))

    bot.send_photo(
        message.chat.id,
        qr,
        caption=
        f"💰 *THÔNG TIN NẠP*\n\n"
        f"🏦 MBBANK\n"
        f"💳 0848794679\n"
        f"📝 Nội dung: {code}\n\n"
        f"💵 Min 10.000đ\n♾ Không giới hạn",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda c: c.data == "confirm")
def confirm_user(call):
    uid = str(call.from_user.id)
    username = call.from_user.username or "Ẩn danh"

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("➕ DUYỆT NẠP", callback_data=f"duyet_{uid}"))

    for admin in ADMIN_IDS:
        bot.send_message(admin,
            f"🔔 Yêu cầu nạp\n@{username}\nID:{uid}\nCode:{pending_codes.get(uid)}",
            reply_markup=markup
        )

    bot.send_message(call.message.chat.id,
        "⏳ Đang chờ admin duyệt.\n"
        "Nếu 5 phút chưa vào xu hãy liên hệ:\n"
        "https://t.me/HLong2002"
    )

@bot.callback_query_handler(func=lambda c: c.data.startswith("duyet_"))
def admin_duyet(call):
    uid = call.data.split("_")[1]
    admin_waiting[call.from_user.id] = uid
    bot.send_message(call.from_user.id, "Nhập số tiền khách chuyển:")

@bot.message_handler(func=lambda m: m.from_user.id in admin_waiting)
def admin_amount(message):
    if not message.text.isdigit():
        return

    amount = int(message.text)
    if amount < 10000:
        return bot.reply_to(message, "❌ Min 10k")

    uid = admin_waiting.pop(message.from_user.id)
    xu = amount // 1000

    user_data[uid]["xu"] += xu
    save_json(DATA_FILE, user_data)

    history_data.setdefault(uid, [])
    history_data[uid].append({
        "time": str(datetime.now()),
        "amount": amount,
        "xu": xu
    })
    save_json(HISTORY_FILE, history_data)

    bot.send_message(uid,
         "━━━━━━━━━━━━━━\n"
        "🎉 *NẠP TIỀN THÀNH CÔNG*\n"
        "━━━━━━━━━━━━━━\n"
        f"💵 Số tiền: {amount}đ\n"
        f"💎 +{xu} xu\n"
        f"💰 Số dư: {user_data[uid]['xu']} xu\n"
        "━━━━━━━━━━━━━━"
    )

    bot.reply_to(message, "✅ Đã cộng xu thành công.")
# ================= ADMIN COMMANDS =================
@bot.message_handler(commands=["adduser"])
def add_user(message):
    if message.from_user.id not in ADMIN_IDS:
        return
    try:
        _, uid, days = message.text.split()
        expire_date = (datetime.now() + timedelta(days=int(days))).strftime("%Y-%m-%d")
        vip_users[uid] = expire_date
        save_json(VIP_FILE, vip_users)
        bot.reply_to(message, "✅ Đã thêm user VIP.")
    except:
        bot.reply_to(message, "Sai cú pháp.")

@bot.message_handler(commands=["themuser"])
def them_user(message):
    if message.from_user.id not in ADMIN_IDS:
        return
    try:
        _, uid = message.text.split()
        vip_users[uid] = "forever"
        save_json(VIP_FILE, vip_users)
        bot.reply_to(message, "🌟 Đã cấp VIP vĩnh viễn.")
    except:
        bot.reply_to(message, "Sai cú pháp.")

@bot.message_handler(commands=["removeuser"])
def remove_user(message):
    if message.from_user.id not in ADMIN_IDS:
        return
    try:
        _, uid = message.text.split()
        if uid in user_data:
            user_data[uid]["xu"] = 0
            save_json(DATA_FILE, user_data)
            bot.reply_to(message, "☠️ Đã xoá xu.")
    except:
        bot.reply_to(message, "Sai cú pháp.")

@bot.message_handler(commands=["listusers"])
def list_users(message):
    if message.from_user.id not in ADMIN_IDS:
        return
    text = "📁 DANH SÁCH USER\n\n"
    for uid, data in user_data.items():
        text += f"{uid} | {data['username']} | {data['xu']} xu\n"
    bot.reply_to(message, text)

@bot.message_handler(commands=["broadcast"])
def broadcast(message):
    if message.from_user.id not in ADMIN_IDS:
        return
    content = message.text.replace("/broadcast ", "")
    count = 0
    for uid in user_data.keys():
        try:
            bot.send_message(uid, f"📢 THÔNG BÁO\n\n{content}")
            count += 1
        except:
            pass
    bot.reply_to(message, f"✅ Đã gửi {count} người.")
print("Bot đang chạy...")
while True:
    try:
        bot.infinity_polling(skip_pending=True, timeout=60, long_polling_timeout=60)
    except Exception as e:
        print("Lỗi kết nối, thử lại sau 5 giây...")
        time.sleep(5)