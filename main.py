import os
import telebot
from collections import defaultdict
import requests
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
AGNES_API_KEY = os.getenv("AGNES_API_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

user_memories = defaultdict(list)
MAX_MEMORY_ROUNDS = 6  

# 1. 网页健康检查服务器配置
class HealthCheckHandler(BaseHTTPRequestHandler):
    # 👇 新增这个方法，专门应对 UptimeRobot 的探测
    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_health_check():
    port = int(os.getenv("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

# 2. 机器人指令逻辑
@bot.message_handler(commands=['start', 'reset'])
def send_welcome(message):
    chat_id = message.chat.id
    welcome_text = "Hi! I'm your English tutor. Let's chat! How was your day today?"
    
    prompt_setup = (
        "从现在开始，你是一位性格随和、像朋友一样的真人外教。你的目标是帮助用户提升日常口语对话能力。\n"
        "# Guidelines\n"
        "1. 语言风格：请使用极其地道的**日常街头/朋友间口语（Casual & Colloquial English）**。拒绝任何死板、正式、教科书式或商务风的表达（例如避免使用 Everything looks good on my end 这种客套话，除非真的在开商务会）。\n"
        "2. 互动方式：每次回答控制在 2 句话以内，像在微信/TG聊天一样简短，别长篇大论。每句话结尾抛出一个超简单的日常问题。\n"
        "3. 双语机制：用户用中文或英文混合时，你用英文互动，必要时可以用极简的中文辅助。\n"
        "# Correction Feedback Loop（硬核接地气纠错）\n"
        "如果用户的英文表达不地道或者有中式英语痕迹，请用最直接、朋友聊天的方式纠正：\n"
        "1. 先用一句话表示理解（如：I get what you mean! / Ah, I see!）\n"
        "2. 【地道表达】：用加粗字体给出 1 个**老外朋友之间最常挂在嘴边、最简单的日常口语**，并用一小句话解释为什么这样更自然。\n"
        "3. 【继续对话】：顺着话题抛出下一个简短问题。"
    )
    
    user_memories[chat_id] = [
        {"role": "system", "content": prompt_setup},
        {"role": "assistant", "content": "Understood. I will act as a patient English tutor, correct your mistakes in Chinese with bold text, and keep our chat natural and fun! Let's chat! How was your day today?"}
    ]
    bot.reply_to(message, welcome_text)

# 3. 机器人聊天核心逻辑
@bot.message_handler(func=lambda message: True)
def chat_with_agnes(message):
    chat_id = message.chat.id
    user_text = message.text

    if chat_id not in user_memories or not user_memories[chat_id]:
        send_welcome(message)
        return

    user_memories[chat_id].append({"role": "user", "content": user_text})
    
    url = "https://apihub.agnes-ai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {AGNES_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "agnes-2.0-flash",
        "messages": user_memories[chat_id]
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        res_data = response.json()

        if "choices" in res_data and res_data["choices"]:
            ai_reply = res_data["choices"][0]["message"]["content"]
            print(f"====== 新消息 ======")
            print(f"用户 [{chat_id}] 说: {user_text}")
            print(f"AI 回复: {ai_reply}")
            print(f"====================")
            
            user_memories[chat_id].append({"role": "assistant", "content": ai_reply})

            while len(user_memories[chat_id]) > (MAX_MEMORY_ROUNDS * 2 + 1):
                user_memories[chat_id].pop(1) 
                user_memories[chat_id].pop(1)

            bot.reply_to(message, ai_reply)
        else:
            error_msg = res_data.get("error", {}).get("message", "Unknown API Error")
            bot.reply_to(message, f"Agnes AI Notice: {error_msg}")
            user_memories[chat_id].pop()

    except Exception as e:
        bot.reply_to(message, f"Connection Notice: {str(e)}")
        if user_memories[chat_id]:
            user_memories[chat_id].pop()

# 4. 完美的唯一入口启动器（必须在最底下）
if __name__ == '__main__':
    print("Starting health check server...")
    threading.Thread(target=run_health_check, daemon=True).start()
    print("Agnes AI English Tutor Bot is running...")
    bot.infinity_polling()
