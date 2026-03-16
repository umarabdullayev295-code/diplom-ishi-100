@echo off
echo ====================================================
echo   AI Media Search (Portable EXE) — Build Script
echo ====================================================

:: 1. Kutubxonalarni tekshirish va o'rnatish
echo [1/3] Dependency-larni tekshirish...
pip install pyinstaller streamlit sentence-transformers faster-whisper faiss-cpu moviepy httpx python-dotenv torch transformers scikit-learn

:: 2. Eski buildlarni tozalash
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build

echo.
echo [2/3] PyInstaller ishga tushmoqda (Custom SPEC fayli orqali)...
:: SPEC fayli orqali hamma narsa avtomatlashtirilgan
pyinstaller --noconfirm run_app.spec

echo.
echo [3/3] Desktopga ko'chirilmoqda...
:: Natijani Desktopga 'video_ai_search' papkasi sifatida ko'chirish
set DESKTOP_PATH=%USERPROFILE%\Desktop\video_ai_search
if exist "%DESKTOP_PATH%" rmdir /s /q "%DESKTOP_PATH%"
xcopy /E /I /Y "dist\video_ai_search" "%DESKTOP_PATH%"

echo.
echo ====================================================
echo   MUVAFFAQIYATLI! Ilova Desktopda 'video_ai_search' papkasida.
echo   Ichidagi 'video_ai_search.exe' ni ishga tushiring.
echo ====================================================
pause
