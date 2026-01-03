@echo off
echo ========================================
echo 会員データバックアップスクリプト
echo ========================================
echo.

REM バックアップディレクトリの作成
if not exist "backups" mkdir backups

REM 日付と時刻を取得
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set date_str=%datetime:~0,8%
set time_str=%datetime:~8,6%
set time_str=%time_str:~0,2%_%time_str:~2,2%_%time_str:~4,2%

REM バックアップファイル名
set backup_file=backups\members_%date_str%_%time_str%.csv

REM バックアップの実行
if exist "members.csv" (
    copy "members.csv" "%backup_file%" >nul
    echo バックアップ完了: %backup_file%
    echo.
    echo バックアップファイル一覧:
    dir /b backups\members_*.csv
) else (
    echo エラー: members.csvが見つかりません
)

echo.
pause


