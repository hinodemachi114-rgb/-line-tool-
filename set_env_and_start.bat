@echo off
echo ========================================
echo 環境変数設定とサーバー起動スクリプト
echo ========================================
echo.
echo 注意: 以下の環境変数に実際の値を設定してください
echo.

REM 実際の値に置き換えてください
set LINE_CHANNEL_ACCESS_TOKEN=aT+8QomDrX8euJP22yke1M1pgBD8ER/IpmWtZhna92w3buRdO8m7/WQJ8tY7nFPzupizDeSimrzpOg8gBGbfbaP2fb1QarvdlaDqxOUcOHta2G9wfVrwklDDeykafUr4k6+WbGdV9yrYAg9S0e/0EgdB04t89/1O/w1cDnyilFU=
set LINE_CHANNEL_SECRET=49711c0305792eaca4262cc61f4e7868

REM セッション管理用の秘密鍵（ランダムな文字列）
REM 生成方法: python -c "import secrets; print(secrets.token_hex(32))"
set FLASK_SECRET_KEY=e7d20b8beaa874b2c7ba2f43f24309ac7afa65a18a90d450c14c52a362234718

REM ngrok URL
set BASE_URL=https://superprecise-devouringly-jairo.ngrok-free.dev

echo 環境変数を設定しました:
echo - LINE_CHANNEL_ACCESS_TOKEN: 設定済み
echo - LINE_CHANNEL_SECRET: 設定済み
echo - FLASK_SECRET_KEY: 設定済み
echo - BASE_URL: %BASE_URL%
echo.
echo サーバーを起動します...
echo.
python server.py

pause

