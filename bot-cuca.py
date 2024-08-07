#!/usr/bin/env python

import logging
import json
import google.generativeai as genai
from typing import Dict

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

with open("/home/syslock/bot-telegram-gemini/settings.cuca.json", "r") as jsonfile:
    settings = json.load(jsonfile)

genai.configure(api_key=settings["GEMINI_API_KEY"])

TOKEN_TELEGRAM = settings["TELEGRAM_TOKEN"]

nombreBot = settings["NOMBRE_BOT"]

model = genai.GenerativeModel('gemini-pro')

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

async def temperatura(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    tempFile = open("/sys/class/thermal/thermal_zone0/temp")
    cpu_temp = tempFile.read()
    tempFile.close()
    cpu_temp = float(cpu_temp)/1000

    await enviar_mensaje(f"La temperatura del CPU es {cpu_temp}", update, context)

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not responder(update, context):
        return

    arroba = settings["MENCION"]
    mensaje = update.message.text.replace(f"{arroba}", nombreBot)

    nombrequien = update.message.from_user.first_name

    response = chat_context.send_message(f"Eres un bot llamado {nombreBot}. No hace falta que te presentes siempre. Usando un parrafo corto lo mas resumido posible, respondele a {nombrequien} el mensaje que te envia: {mensaje}.")

    await enviar_mensaje(response.text, update, context)

def responder(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    # Comprobar si lo llamaron por su nombre
    mencionNombre = nombreBot.lower() in update.message.text.lower()
    
    if mencionNombre:
        return True

    # Comprobar si respondieron a uno de sus mensajes
    mencionReply = update.message.reply_to_message and update.message.reply_to_message.from_user.id == context.bot.id
    
    if mencionReply:
        return True
    
    # Comprobar si hicieron una mencion
    arroba = settings["MENCION"]

    if update.message.entities:
        for entity in update.message.entities:
            if entity.type == "mention" and arroba in update.message.text:
                return True
   
    return False

async def borrar_historial(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Borra el historial de Gemini
    """
    
    global chat_context
    chat_context = model.start_chat(history=[])
    mensaje = "Historial de consultas borrado"
    await enviar_mensaje(mensaje, update, context)
    
async def concatenar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Concatena dos números
    """
    try:
        number1 = int(context.args[0])
        number2 = int(context.args[1])
        result = str(number1)+str(number2)
        await update.message.reply_text(result)
    except (IndexError, ValueError):
        await update.message.reply_text('Tenés que pasarme dos números')

async def mostrar_ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Muestra la ayuda del bot
    """
    presentacion = f"Soy {nombreBot}, tu asistente virtual. Para hablar conmigo solo debes mencionar mi nombre. Uso la IA de Gemini para poder ayudarte. \n" 
    mensaje =  r"""
                /borrar_historial borra el historial de la conversación de mi memoria.
                /suma n1 n2 concatena dos números.
                /ayuda muestra este texto de ayuda.
                """
    mensaje = presentacion + mensaje
    
    await enviar_mensaje(mensaje, update, context)

async def enviar_mensaje(text, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    await update.message.reply_text(text)
    #print(update)
    """if update.message.reply_to_message:
        await update.message.reply_text(text)
    elif update.message.chat.type == "supergroup":
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text=text,
            message_thread_id=update.message.message_thread_id
        )
    else:
        await context.bot.send_message(
            update.message.chat_id,
            text
        )"""

def main() -> None:
    """Run the bot."""

    application = Application.builder().token(TOKEN_TELEGRAM).build()

    global chat_context
    chat_context = model.start_chat(history=[])

    # Handlers de comandos
    #application.add_handler(CommandHandler("temperatura", temperatura))
    application.add_handler(CommandHandler("suma", concatenar))
    application.add_handler(CommandHandler("ayuda", mostrar_ayuda))
    application.add_handler(CommandHandler("borrar_historial", borrar_historial))

    # Handler de mensajes
    application.add_handler(MessageHandler(~filters.COMMAND, chat))    

    # Mantener el bot en ejecución
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
