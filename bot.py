import asyncio
import os
import requests
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ================= НАСТРОЙКИ =================
TELEGRAM_TOKEN = os.getenv("TG_BOT_TOKEN")
GITHUB_TOKEN = os.getenv("GH_PAT")                    # Personal Access Token
REPO_OWNER = "твой_логин"                             # Например: "username"
REPO_NAME = "название_репозитория"                   # Например: "vless-collector"
WORKFLOW_FILE = "main.yml"                            # или как у тебя называется

# ============================================

async def run_workflow():
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/workflows/{WORKFLOW_FILE}/dispatches"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {GITHUB_TOKEN}",
    }
    data = {"ref": "main"}

    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 204:
        print(f"[{datetime.now()}] Workflow успешно запущен")
        return True
    else:
        print(f"Ошибка: {response.status_code} - {response.text}")
        return False


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Бот запущен и готов к работе.\n\nКоманды:\n/run — запустить workflow вручную")

async def run_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 Запускаю GitHub Workflow...")
    success = await run_workflow()
    if success:
        await update.message.reply_text("✅ Workflow успешно запущен!")
    else:
        await update.message.reply_text("❌ Не удалось запустить workflow")


async def scheduled_run(context: ContextTypes.DEFAULT_TYPE):
    print(f"[{datetime.now()}] Автоматический запуск по расписанию...")
    await run_workflow()


async def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("run", run_command))

    # Запуск по расписанию каждые 15 минут
    job_queue = app.job_queue
    job_queue.run_repeating(scheduled_run, interval=900, first=10)  # 900 секунд = 15 минут

    print("Бот запущен...")
    await app.run_polling()


if __name__ == "__main__":
    asyncio.run(main())
