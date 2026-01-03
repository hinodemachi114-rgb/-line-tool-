# 環境変数の設定方法

## セキュリティ強化のため、機密情報を環境変数で管理

### 設定方法

#### PowerShellの場合
```powershell
$env:LINE_CHANNEL_ACCESS_TOKEN="your_channel_access_token"
$env:LINE_CHANNEL_SECRET="your_channel_secret"
$env:FLASK_SECRET_KEY="your_secret_key_here"
$env:BASE_URL="https://superprecise-devouringly-jairo.ngrok-free.dev"
```

#### CMDの場合
```cmd
set LINE_CHANNEL_ACCESS_TOKEN=your_channel_access_token
set LINE_CHANNEL_SECRET=your_channel_secret
set FLASK_SECRET_KEY=your_secret_key_here
set BASE_URL=https://superprecise-devouringly-jairo.ngrok-free.dev
```

### サーバー起動

環境変数を設定した後、サーバーを起動:
```bash
python server.py
```

### 注意事項

⚠️ **環境変数が設定されていない場合、デフォルト値が使用されます。**
本番環境では必ず環境変数を設定してください。

⚠️ **FLASK_SECRET_KEYは、セッション管理とCSRF対策に使用されます。**
ランダムな文字列を生成して設定してください:
```python
import secrets
print(secrets.token_hex(32))
```

