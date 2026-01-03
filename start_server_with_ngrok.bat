@echo off
echo ========================================
echo LINE Bot サーバー起動スクリプト（ngrok使用）
echo ========================================
echo.

REM ngrokがインストールされているか確認
where ngrok >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [エラー] ngrokが見つかりません。
    echo.
    echo ngrokのインストール方法:
    echo 1. https://ngrok.com/download からngrokをダウンロード
    echo 2. ngrok.exeをこのフォルダに配置するか、PATHに追加してください
    echo.
    pause
    exit /b 1
)

echo [1/4] 環境変数を設定しています...
set BASE_URL=https://superprecise-devouringly-jairo.ngrok-free.dev
echo BASE_URL = %BASE_URL%
echo.

echo [2/4] Flaskサーバーを起動しています...
start "Flask Server" cmd /k "python server.py"

echo [3/4] 5秒待機中（サーバー起動を待機）...
timeout /t 5 /nobreak >nul

echo [4/4] ngrokトンネルを開始しています...
echo.
echo ========================================
echo 以下のURLが外部公開されます:
echo ========================================
echo Webhook URL: %BASE_URL%/callback
echo フォームURL: %BASE_URL%/register
echo.
echo ngrokの画面で「Forwarding」のURLを確認してください
echo サーバーが起動したら、LINE DevelopersでWebhook URLを設定してください
echo ========================================
echo.
ngrok http 5000

pause

