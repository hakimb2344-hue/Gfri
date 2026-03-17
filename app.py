import telebot
from yt_dlp import YoutubeDL
import os

# التوكن الخاص بك الذي زودتني به
API_TOKEN = '8338706916:AAEqNZgtFWCcIaazYZsPIfwxrXh34PWQ70E'
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    user_name = message.from_user.first_name
    welcome_text = (
        f"أهلاً بك يا **{user_name}** في بوت تحميل الفيديو! 🌟\n\n"
        "يمكنني تحميل الفيديوهات من (YouTube, TikTok, Instagram, Facebook).\n\n"
        "**فقط أرسل لي رابط الفيديو، وسأقوم بالباقي! 📥**"
    )
    bot.reply_to(message, welcome_text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def handle_video_download(message):
    url = message.text
    
    # التحقق من أن النص المرسل هو رابط
    if not url.startswith("http"):
        bot.reply_to(message, "الرجاء إرسال رابط صحيح يبدأ بـ http أو https 🔗")
        return

    # إرسال رسالة "جاري المعالجة" للمستخدم
    status_msg = bot.reply_to(message, "⏳ جاري جلب الفيديو والمعالجة... انتظر قليلاً")
    
    # إعدادات التنزيل (أفضل جودة ممكنة)
    ydl_opts = {
        'format': 'best',
        'outtmpl': f'video_{message.chat.id}.%(ext)s', # اسم ملف فريد لكل مستخدم
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            # عملية التنزيل الفعلي من السوشل ميديا إلى جهازك
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        
        # إرسال الملف المحمل إلى تلجرام
        with open(filename, 'rb') as video:
            bot.send_video(message.chat.id, video, caption="✅ تم التحميل بنجاح بواسطة بوتك!")
        
        # حذف الملف من جهازك بعد الإرسال لتوفير المساحة
        if os.path.exists(filename):
            os.remove(filename)
            
        # حذف رسالة "جاري المعالجة"
        bot.delete_message(message.chat.id, status_msg.message_id)

    except Exception as e:
        bot.edit_message_text(f"❌ عذراً، تعذر تحميل هذا الرابط.\nالسبب: {str(e)[:50]}...", message.chat.id, status_msg.message_id)
        # تنظيف الملف في حال وجود خطأ
        if 'filename' in locals() and os.path.exists(filename):
            os.remove(filename)

print("البوت يعمل الآن... اضغط Ctrl+C للإيقاف")
bot.polling(none_stop=True)
