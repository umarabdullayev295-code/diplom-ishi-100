import sys
import streamlit.web.cli as stcli
import os
import subprocess
import logging

# Xatoliklarni faylga yozib borish (diagnostika uchun)
logging.basicConfig(
    filename='app_debug.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def resolve_path(path):
    """ EXE ichidagi fayllar yo'lini aniqlash uchun """
    if getattr(sys, 'frozen', False):
        basedir = sys._MEIPASS
    else:
        basedir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(basedir, path)

if __name__ == "__main__":
    try:
        logging.info("Dastur ishga tushmoqda...")
        
        # app.py yo'lini aniqlash
        app_path = resolve_path(os.path.join("video_ai_search", "app.py"))
        if not os.path.exists(app_path):
            logging.error(f"app.py topilmadi: {app_path}")
            # Zaxira yo'l
            app_path = resolve_path("app.py")
            
        logging.info(f"App yo'li: {app_path}")

        # .env faylni yuklash
        env_path = resolve_path(".env")
        if os.path.exists(env_path):
            from dotenv import load_dotenv
            load_dotenv(env_path)
            logging.info(".env yuklandi")

        # Streamlit argumentlari
        sys.argv = [
            "streamlit",
            "run",
            app_path,
            "--global.developmentMode=false",
            "--server.port=8501",
            "--server.address=localhost",
            "--browser.gatherUsageStats=false"
        ]
        
        logging.info("Streamlit server ishga tushirilmoqda...")
        stcli.main()
        
    except Exception as e:
        logging.exception("Portativ EXE ishga tushishida xatolik yuz berdi:")
        print(f"\nFATAL ERROR: {e}")
        print("Tafsilotlar uchun 'app_debug.log' faylini ko'ring.")
        input("\nYopish uchun Enter bosing...")
