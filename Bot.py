import telebot
import json
from telebot.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

# تعريف البوت مع التوكن الخاص به
API_TOKEN = "7965335827:AAGZvqTkYkb-xnMCH2iWKLMyF2SpgLynlrE"
bot = telebot.TeleBot(API_TOKEN)

# تعريف ملف تخزين البيانات
DATA_FILE = "users_data.json"

# تحميل البيانات أو إنشاء ملف جديد
try:
    with open(DATA_FILE, "r") as file:
        users_data = json.load(file)
except FileNotFoundError:
    users_data = {}

# دالة لحفظ البيانات إلى الملف
def save_data():
    with open(DATA_FILE, "w") as file:
        json.dump(users_data, file, indent=4)

# دالة لإضافة بيانات المستخدم
def add_user(user_id, username=None, balance=0):
    if user_id not in users_data:
        users_data[user_id] = {
            "user_id": user_id,  # إضافة الـ user_id
            "username": username or "غير متاح",  # إذا لم يكن اسم المستخدم موجودًا
            "balance": balance
        }
        save_data()
# دالة لإنشاء لوحة المفاتيح الرئيسية
def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("💳 شحن رصيد في البوت", "💸 سحب حوالة")
    markup.add("💼 شحن حساب ichancy", "📊 معلومات حسابي")
    markup.add("📜 سجل المعاملات", "💰 رصيد حسابي")
    markup.add("📞 التواصل مع الدعم الفني")
    return markup

# دالة التحقق أو إنشاء حساب
@bot.message_handler(commands=["start"])
def start(message):
    user_id = str(message.from_user.id)
    if user_id in users_data:
        bot.send_message(message.chat.id, "مرحبًا بك مجددًا!", reply_markup=main_menu())
    else:
        bot.send_message(message.chat.id, "مرحبًا بك! يجب إنشاء حساب جديد.")
        msg = bot.send_message(message.chat.id, "👤 أدخل اسم المستخدم:")
        bot.register_next_step_handler(msg, get_username)

# طلب اسم المستخدم
def get_username(message):
    username = message.text
    user_id = str(message.from_user.id)
    users_data[user_id] = {"username": username}
    msg = bot.send_message(message.chat.id, "🔒 أدخل كلمة مرور قوية مكونة من 8 أحرف، رقم، ورمز:")
    bot.register_next_step_handler(msg, get_password)

# طلب كلمة المرور
def get_password(message):
    password = message.text
    if len(password) < 8 or not any(char.isdigit() for char in password) or not any(char in "!@#$%^&*()-_+=" for char in password):
        msg = bot.send_message(message.chat.id, "❌ كلمة المرور ضعيفة. حاول مجددًا:")
        bot.register_next_step_handler(msg, get_password)
        return

    user_id = str(message.from_user.id)
    users_data[user_id]["password"] = password
    msg = bot.send_message(message.chat.id, "📲 أدخل رقم سيرياتيل كاش (10 أرقام):")
    bot.register_next_step_handler(msg, get_syriatel_number)

# طلب رقم سيرياتيل كاش
def get_syriatel_number(message):
    syriatel_number = message.text
    if len(syriatel_number) != 10 or not syriatel_number.isdigit():
        msg = bot.send_message(message.chat.id, "❌ الرقم غير صالح. حاول مجددًا:")
        bot.register_next_step_handler(msg, get_syriatel_number)
        return

    user_id = str(message.from_user.id)
    users_data[user_id]["syriatel_number"] = syriatel_number
    users_data[user_id]["balance"] = 0
    save_data()
    bot.send_message(message.chat.id, "✅ تم إنشاء حسابك بنجاح!", reply_markup=main_menu())

# التعامل مع زر شحن البوت 
# التعامل مع زر شحن البوت 
@bot.message_handler(func=lambda message: message.text == "💳 شحن رصيد في البوت")
def charge_balance(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("سيرياتيل كاش", "بايير", "رجوع")
    bot.send_message(message.chat.id, "💳 اختر طريقة الشحن:", reply_markup=markup)

# اختيار سيرياتيل كاش
@bot.message_handler(func=lambda message: message.text == "سيرياتيل كاش")
def syriatel_cash(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("❌ إلغاء", callback_data="cancel_charge"))
  bot.send_message(
        message.chat.id,
        "📲 قم بالتحويل (يدوي) إلى التاجر صاحب الرقم 13310093\n\n"
        "💡 أقل مبلغ شحن للرصيد هو 15,000\n\n"
        "✍️ أدخل رقم عملية التحويل:",
        reply_markup=markup
    )
    bot.register_next_step_handler(message, get_transaction_id)

# طلب رقم العملية
def get_transaction_id(message):
    transaction_id = message.text
    if len(transaction_id) not in [12, 15] or not transaction_id.isdigit():
        msg = bot.send_message(message.chat.id, "❌ الرقم غير صحيح. حاول مجددًا:")
        bot.register_next_step_handler(msg, get_transaction_id)
        return

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("❌ إلغاء", callback_data="cancel_charge"))
    msg = bot.send_message(
        message.chat.id,
        "💵 أدخل مبلغ التحويل:",
        reply_markup=markup
    )
    bot.register_next_step_handler(msg, process_transaction, transaction_id)

# معالجة رقم العملية والمبلغ
def process_transaction(message, transaction_id):
    amount = message.text
    try:
        amount = float(amount)
    except ValueError:
        msg = bot.send_message(message.chat.id, "❌ المبلغ غير صالح. حاول مجددًا:")
        bot.register_next_step_handler(msg, process_transaction, transaction_id)
        return

    # الحصول على username
    username = message.from_user.username or "غير متاح"  # تأكد من التعامل مع حالة عدم وجود username

    # الحصول على ID المستخدم
    user_id = message.from_user.id
    
    admin_id = @FastBet_Robert  # أيدي المشرف
    bot.send_message(
        admin_id,
        f"🚨 طلب شحن جديد 🚨\n\n"
        f"رقم العملية: {transaction_id}\n"
        f"المبلغ: {amount}\n"
        f"ID المستخدم: {user_id}\n"
        f"اسم المستخدم: @{username}",
        reply_markup=admin_buttons(transaction_id, amount, user_id)  # تمرير username هنا
    )
    bot.send_message(message.chat.id, "✅ تم إرسال طلبك إلى المشرف. يرجى الانتظار.", reply_markup=main_menu())

# لوحة أزرار المشرف
def admin_buttons(transaction_id, amount, user_id):
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("✅ تم الشحن", callback_data=f"approve_{transaction_id}_{amount}_{user_id}"),
        InlineKeyboardButton("❌ إلغاء العملية", callback_data=f"cancel_transaction_{transaction_id}_{user_id}")
    )
    return markup

# التعامل مع ردود المشرف (إضافة دعم زر إلغاء العملية)
@bot.callback_query_handler(func=lambda call: call.data.startswith("approve_") or call.data.startswith("cancel_transaction_"))
def handle_admin_response(call):
    data = call.data.split("_")
    action = data[0]
    
    if action == "approve":
        transaction_id = data[1]
        amount = float(data[2])
        user_id = data[3]
        if user_id not in users_data:
            users_data[user_id] = {"balance": 0}
        users_data[user_id]["balance"] += amount
        save_data()
        bot.send_message(user_id, f"✅ تم شحن حسابك بمبلغ: {amount}")
        bot.edit_message_text("✅ تم التعامل مع الطلب.", call.message.chat.id, call.message.message_id)

    elif action == "cancel_transaction":
        transaction_id = data[1]
        user_id = data[2]
        bot.send_message(user_id, "❌ رقم عملية التحويل غير صحيح أو مستخدم مسبقًا.")
        bot.edit_message_text("✅ تم إلغاء العملية.", call.message.chat.id, call.message.message_id)

# التعامل مع زر الإلغاء
@bot.callback_query_handler(func=lambda call: call.data == "cancel_charge")
def cancel_charge(call):
    bot.send_message(
        call.message.chat.id,
        "❌ تم إلغاء عملية الشحن. يمكنك العودة إلى القائمة الرئيسية.",
        reply_markup=main_menu()
    )


# التعامل مع زر "💰 رصيد حسابي"
@bot.message_handler(func=lambda message: message.text == "💰 رصيد حسابي")
def check_balance(message):
    user_id = str(message.from_user.id)
    if user_id in users_data:
        balance = users_data[user_id].get("balance", 0)
        bot.send_message(message.chat.id, f"💰 رصيد حسابك الحالي هو: {balance} ل.س")
    else:
        bot.send_message(message.chat.id, "❌ ليس لديك حساب. يرجى إنشاء حساب جديد أولاً.")
      # التعامل مع زر "📞 التواصل مع الدعم الفني"
@bot.message_handler(func=lambda message: message.text == "📞 التواصل مع الدعم الفني")
def contact_support(message):
    bot.send_message(message.chat.id, "✍️ اكتب رسالة تتضمن مشكلتك وسيتم إرسالها للدعم الفني بعد التأكيد.")
    bot.register_next_step_handler(message, ask_for_confirmation)

# طلب تأكيد أو إلغاء إرسال الرسالة
def ask_for_confirmation(message):
    user_message = message.text  # تخزين الرسالة النصية مؤقتًا
    # إنشاء أزرار تأكيد وإلغاء
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("✅ تأكيد", callback_data=f"confirm|{message.chat.id}|{user_message}"),
        InlineKeyboardButton("❌ إلغاء", callback_data="cancel")
    )
    # عرض الرسالة مع الأزرار
    bot.send_message(
        message.chat.id,
        f"📩 رسالتك:\n\n{user_message}\n\nهل ترغب في إرسالها؟",
        reply_markup=markup
    )

# التعامل مع تأكيد أو إلغاء
@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm|") or call.data == "cancel")
def handle_confirmation(call):
    if call.data.startswith("confirm|"):
        # إذا تم الضغط على زر "تأكيد"
        _, user_chat_id, user_message = call.data.split("|", 2)  # استخراج بيانات الرسالة
        forward_to_admin(call.message, user_message, int(user_chat_id))
    elif call.data == "cancel":
        # إذا تم الضغط على زر "إلغاء"
        bot.send_message(call.message.chat.id, "❌ تم إلغاء الإرسال.", reply_markup=main_menu())

# إرسال رسالة المستخدم إلى المشرف
def forward_to_admin(message, user_message, user_chat_id):
    user_username = message.chat.username or "لا يوجد اسم مستخدم"
    admin_id = 5504502257  # أيدي المشرف

    # إرسال الرسالة للمشرف
    bot.send_message(
        admin_id,
        f"🚨 رسالة جديدة من المستخدم 🚨\n\n"
        f"📩 الرسالة: {user_message}\n"
        f"👤 المستخدم: @{user_username} (ID: {user_chat_id})",
        reply_markup=admin_reply_button(user_chat_id)
    )
    # إخطار المستخدم بأن الرسالة أُرسلت
    bot.send_message(
        user_chat_id,
        "✅ تم إرسال رسالتك إلى الدعم الفني. يرجى الانتظار للرد.",
        reply_markup=main_menu()
    )

# إنشاء زر الرد من المشرف
def admin_reply_button(user_chat_id):
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("✉️ الرد على المستخدم", callback_data=f"reply_{user_chat_id}")
    )
    return markup

# التعامل مع رد المشرف
@bot.callback_query_handler(func=lambda call: call.data.startswith("reply_"))
def handle_admin_reply(call):
    user_chat_id = call.data.split("_")[1]
    msg = bot.send_message(call.message.chat.id, "✍️ اكتب رسالة الرد للمستخدم:")
    bot.register_next_step_handler(msg, send_reply_to_user, user_chat_id)

# إرسال الرد من المشرف إلى المستخدم
def send_reply_to_user(message, user_chat_id):
    admin_message = message.text
    bot.send_message(
        user_chat_id,
        f"📩 رسالة من الدعم الفني:\n\n{admin_message}\n\n🤝 شكراً لتواصلك معنا!"
    )
    bot.send_message(
        message.chat.id,
        "✅ تم إرسال الرد إلى المستخدم.",
        reply_markup=main_menu()
    )

# دالة لإنشاء لوحة المفاتيح الرئيسية
def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("💳 شحن رصيد في البوت", "💸 سحب حوالة")
    markup.add("💼 شحن حساب ichancy", "📊 معلومات حسابي")
    markup.add("📜 سجل المعاملات", "💰 رصيد حسابي")
    markup.add("📞 التواصل مع الدعم الفني",)  # إضافة خيار لعبة الحظ
    return markup
# دالة التحقق أو إنشاء حساب



# التعامل مع زر "💸 سحب حوالة"
# التعامل مع زر "💸 سحب حوالة"
@bot.message_handler(func=lambda message: message.text == "💸 سحب حوالة")
def withdraw_request(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("❌ إلغاء", callback_data="cancel_withdraw"))
    bot.send_message(
        message.chat.id,
        "💰 أدخل المبلغ الذي ترغب بسحبه من البوت:",
        reply_markup=markup
    )
    bot.register_next_step_handler(message, process_withdraw_amount)
  # معالجة إدخال المبلغ
def process_withdraw_amount(message):
    try:
        amount = float(message.text)
        user_id = str(message.from_user.id)

        if amount <= 0:
            bot.send_message(message.chat.id, "❌ المبلغ يجب أن يكون أكبر من الصفر. حاول مرة أخرى.")
            return

        if user_id not in users_data or users_data[user_id]["balance"] < amount:
            bot.send_message(
                message.chat.id, 
                "❌ رصيدك غير كافٍ لإجراء هذه العملية. يرجى التحقق من رصيدك."
            )
            return

        users_data[user_id]["withdraw_amount"] = amount
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("❌ إلغاء", callback_data="cancel_withdraw"))
        bot.send_message(
            message.chat.id, 
            "📲 أدخل رقم سيرياتيل كاش الذي ترغب بسحب الرصيد إليه:",
            reply_markup=markup
        )
        bot.register_next_step_handler(message, process_withdraw_number)
    except ValueError:
        bot.send_message(message.chat.id, "❌ يرجى إدخال مبلغ صالح.")

# معالجة إدخال رقم سيرياتيل كاش
def process_withdraw_number(message):
    withdraw_number = message.text
    user_id = str(message.from_user.id)

    if len(withdraw_number) != 10 or not withdraw_number.isdigit():
        bot.send_message(message.chat.id, "❌ رقم سيرياتيل كاش غير صحيح. يجب أن يكون مكوناً من 10 أرقام.")
        return

    amount = users_data[user_id]["withdraw_amount"]
    users_data[user_id]["balance"] -= amount  # خصم الرصيد
    admin_id = @FastBet_Robert  # أيدي المشرف

    # إرسال الطلب للمشرف
    bot.send_message(
        admin_id,
        f"🚨 طلب سحب جديد 🚨\n\n"
        f"💳 المبلغ: {amount}\n"
        f"📲 رقم سيرياتيل كاش: {withdraw_number}\n"
        f"👤 المستخدم: @{message.from_user.username or 'لا يوجد اسم مستخدم'} (ID: {user_id})\n"
        f"💰 الرصيد المتبقي: {users_data[user_id]['balance']}",
        reply_markup=admin_withdraw_button(user_id)
    )

    bot.send_message(
        message.chat.id,
        f"✅ تم إرسال طلب السحب إلى المشرف. يرجى الانتظار حتى يتم معالجة الحوالة.",
        reply_markup=main_menu()
    )

# إنشاء زر تم السحب للمشرف
def admin_withdraw_button(user_id):
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("✅ تم السحب", callback_data=f"withdraw_done_{user_id}")
    )
    return markup

# التعامل مع تأكيد السحب من المشرف
@bot.callback_query_handler(func=lambda call: call.data.startswith("withdraw_done_"))
def handle_withdraw_done(call):
    user_id = call.data.split("_")[2]
    bot.send_message(
        user_id,
        "✅ تم سحب الرصيد من حسابك ومعالجة الحوالة بنجاح. شكراً لاستخدامك خدماتنا!"
    )
    bot.send_message(
        call.message.chat.id,
        "✅ تم تأكيد عملية السحب وإعلام المستخدم."
    )

# التعامل مع زر الإلغاء
@bot.callback_query_handler(func=lambda call: call.data == "cancel_withdraw")
def cancel_withdraw(call):
    bot.send_message(
        call.message.chat.id,
        "❌ تم إلغاء عملية السحب. يمكنك العودة إلى القائمة الرئيسية.",
        reply_markup=main_menu()
    )


# معالجة زر "معلومات حسابي"
@bot.message_handler(func=lambda message: message.text == "📊 معلومات حسابي")
def account_info(message):
    user_id = str(message.from_user.id)

    # التحقق إذا كان المستخدم موجودًا في البيانات
    if user_id in users_data:
        user_info = users_data[user_id]
        username = user_info['username']
        syriatel_number = user_info['syriatel_number']
        balance = user_info['balance']
        
        info_message = f"""📊 *معلومات حسابي*:
        
🔑 اسم المستخدم: {username}
📱 رقم سيرياتيل كاش: {syriatel_number}
💰 الرصيد الحالي: {balance} SYP
📜 سجل المعاملات:

        """
        bot.send_message(user_id, info_message, parse_mode='Markdown')
    else:
        bot.send_message(user_id, "لم يتم العثور على حسابك. من فضلك قم بإنشاء حساب أولًا باستخدام /start.")

# بدء 22
# معالج لتشغيل شحن الرصيد
@bot.message_handler(func=lambda message: message.text == "💼 شحن حساب ichancy")
def charge_balance(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("شحن رصيد ichancy⚡", "سحب رصيد ichancy⚡", "معلومات حساب ichancy", "رجوع")
    bot.send_message(message.chat.id, "💳 اختر طريقة حدمتك:", reply_markup=markup)

# معالج للرجوع إلى القائمة الرئيسية
@bot.message_handler(func=lambda message: message.text == "رجوع")
def go_back(message):
    markup = main_menu()  # استخدام دالة القائمة الرئيسية هنا
    bot.send_message(message.chat.id, "🔙 عدت إلى القائمة الرئيسية:", reply_markup=markup)

# معالج لعرض معلومات الحساب
@bot.message_handler(func=lambda message: message.text == "معلومات حساب ichancy")
def account_info(message):
    info_message = (
        "🔐 معلومات حسابك في ايشانسي ⚡️\n\n"
        "👤 Username: K.Test01\n"
        "🔑 Password: 12345Kk@\n"
        "🆔 Id: 109788974\n"
        "💰 Balance: 0"
    )
    bot.send_message(message.chat.id, info_message)

# معالج لطلب المبلغ لشحن الرصيد
@bot.message_handler(func=lambda message: message.text == "شحن رصيد ichancy⚡")
def ask_for_amount(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("إلغاء العملية")
    bot.send_message(message.chat.id, "🔢 من فضلك أدخل المبلغ الذي ترغب في شحنه، أو اضغط 'إلغاء العملية' للرجوع.", reply_markup=markup)

# معالجة إلغاء العملية
@bot.message_handler(func=lambda message: message.text == "إلغاء العملية")
def cancel_operation(message):
    markup = main_menu()  # العودة إلى القائمة الرئيسية
    bot.send_message(message.chat.id, "❌ تم إلغاء العملية والرجوع إلى القائمة الرئيسية.", reply_markup=markup)


#تعديل22

@bot.message_handler(func=lambda message: message.text == "سحب رصيد ichancy⚡")
def withdraw_balance(message):
    bot.send_message(message.chat.id, "🚫 رصيد ايشانسي الخاص بك هو 0. لا يمكنك السحب.")

@bot.message_handler(func=lambda message: message.text == "📜 سجل المعاملات")
def withdraw_balance(message):
    bot.send_message(message.chat.id, "سجل المعاملات غير متوفر حاليا ")

# تعديل 2 
# قائمة لتخزين معرفات المشرفين
ADMIN_IDS = {@FastBet_Robert}  # استبدل هذه الأعداد بمعرفات المشرفين الحقيقيين


# دالة للتحقق مما إذا كان المستخدم مشرفًا
def is_admin(user_id):
    return user_id in ADMIN_IDS

# دالة لمعالجة الرسائل
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    if message.text.startswith("/send_id"):
        parts = message.text.split(maxsplit=2)  # تقسيم الرسالة إلى 3 أجزاء كحد أقصى
        if len(parts) < 3:
            bot.send_message(message.chat.id, "❌ صيغة الرسالة غير صحيحة. استخدم: /send_id [user_id] [your_message]")
            return

        user_id = parts[1]
        user_message = parts[2]

        try:
            bot.send_message(user_id, f"📩 رسالة من الدعم:\n\n{user_message}")
            bot.send_message(message.chat.id, "✅ تم إرسال الرسالة بنجاح.")
        except Exception as e:
            bot.send_message(message.chat.id, "❌ حدث خطأ أثناء إرسال الرسالة. تأكد من أن معرف المستخدم صحيح.")

# تشغيل البوت
bot.polling()
