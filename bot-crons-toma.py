import requests
import json
import sys

with open("/home/syslock/bot-telegram-gemini/settings.cuca.json", "r") as jsonfile:
    settings = json.load(jsonfile)

TELEGRAM_TOKEN = settings["TELEGRAM_TOKEN"]

threads = {
      "general": "1",
      "organizacion": settings["THREAD_ORGANIZACION"],
      "electronica": settings["THREAD_ELECTRONICA"],
      "softhard": settings["THREAD_SOFTHARD"],
      "retro": settings["THREAD_RETRO"],
}

def main() -> None:

        if (len(sys.argv) != 3):
                print("Error: Se deben pasar la pregunta y el canal como parámetros.")
                return

        pregunta = sys.argv[1]
        canal = sys.argv[2]

        if (canal in threads):
                thread_id = threads[canal]
        else:
              print("Error: canal no encontrado.")
              return
        
        chat_id = settings["CHAT_ID"]
              
        message_data = {
                "chat_id": chat_id,
                "message_thread_id": thread_id, 
                "is_anonymous": False,
                "question": pregunta,
                "options": json.dumps(['Si', 'No', 'Tal vez']),
                "type": "regular"
        }
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPoll", data=message_data)


if __name__ == "__main__":
    main()