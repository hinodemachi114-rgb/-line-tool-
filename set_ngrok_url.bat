@echo off
echo ========================================
echo ngrok URL設定スクリプト
echo ========================================
echo.
echo ngrok URLを環境変数に設定します
echo URL: https://superprecise-devouringly-jairo.ngrok-free.dev
echo.

set BASE_URL=https://superprecise-devouringly-jairo.ngrok-free.dev
echo BASE_URL環境変数を設定しました: %BASE_URL%
echo.
echo サーバーを起動します...
echo.
python server.py

pause

