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

echo [1/3] Flaskサーバーを起動しています...
start "Flask Server" cmd /k "python server.py"

echo [2/3] 5秒待機中...
timeout /t 5 /nobreak >nul

echo [3/3] ngrokトンネルを開始しています...
echo.
echo ========================================
echo 以下のURLが外部公開されます:
echo ========================================
echo.
echo ngrokの画面に表示される「Forwarding」のURL（https://...）をコピーしてください
echo その後、以下のコマンドで環境変数を設定してください:
echo.
echo PowerShellの場合:
echo   $env:BASE_URL="https://xxxx-xxxx.ngrok-free.app"
echo   python server.py
echo.
echo CMDの場合:
echo   set BASE_URL=https://xxxx-xxxx.ngrok-free.app
echo   python server.py
echo.
echo ========================================
echo.
ngrok http 5000

pause

