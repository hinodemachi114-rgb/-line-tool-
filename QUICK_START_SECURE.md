# セキュアな起動手順

## 簡単な起動方法

### 方法1: バッチファイルを使用（推奨）

環境変数を設定してサーバーを起動:

**PowerShellの場合:**
```powershell
.\set_env_and_start.bat
```

**CMD（コマンドプロンプト）の場合:**
```cmd
set_env_and_start.bat
```

**注意**: このバッチファイルには実際のトークンが含まれています。本番環境では環境変数を直接設定してください。

### 方法2: 手動で環境変数を設定

#### CMDで設定
```cmd
set LINE_CHANNEL_ACCESS_TOKEN=aT+8QomDrX8euJP22yke1M1pgBD8ER/IpmWtZhna92w3buRdO8m7/WQJ8tY7nFPzupizDeSimrzpOg8gBGbfbaP2fb1QarvdlaDqxOUcOHta2G9wfVrwklDDeykafUr4k6+WbGdV9yrYAg9S0e/0EgdB04t89/1O/w1cDnyilFU=
set LINE_CHANNEL_SECRET=49711c0305792eaca4262cc61f4e7868
set FLASK_SECRET_KEY=生成したランダム文字列
set BASE_URL=https://superprecise-devouringly-jairo.ngrok-free.dev
python server.py
```

#### PowerShellで設定
```powershell
$env:LINE_CHANNEL_ACCESS_TOKEN="aT+8QomDrX8euJP22yke1M1pgBD8ER/IpmWtZhna92w3buRdO8m7/WQJ8tY7nFPzupizDeSimrzpOg8gBGbfbaP2fb1QarvdlaDqxOUcOHta2G9wfVrwklDDeykafUr4k6+WbGdV9yrYAg9S0e/0EgdB04t89/1O/w1cDnyilFU="
$env:LINE_CHANNEL_SECRET="49711c0305792eaca4262cc61f4e7868"
$env:FLASK_SECRET_KEY="生成したランダム文字列"
$env:BASE_URL="https://superprecise-devouringly-jairo.ngrok-free.dev"
python server.py
```

### FLASK_SECRET_KEYの生成

セキュリティのため、ランダムな文字列を生成してください:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

生成された文字列を `FLASK_SECRET_KEY` に設定してください。

## セキュリティ機能

現在の実装には以下のセキュリティ対策が含まれています:

- ✅ 機密情報の環境変数管理
- ✅ ログからの機密情報除外
- ✅ 入力値の検証とサニタイズ（XSS対策）
- ✅ CSRF対策
- ✅ レート制限
- ✅ user_idの形式検証
- ✅ セキュリティヘッダー
- ✅ セッション管理

詳細は `SECURITY_IMPROVEMENTS.md` を参照してください。

