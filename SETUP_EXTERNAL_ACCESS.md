# 外部公開の設定方法

## 方法1: ngrokを使用（推奨・簡単）

### 1. ngrokのインストール

1. https://ngrok.com/download からngrokをダウンロード
2. ngrok.exeをこのフォルダ（line_tool）に配置
3. （オプション）ngrokアカウントを作成して認証トークンを設定（無料プランで十分）

```bash
# ngrokアカウント作成後、認証トークンを設定（オプション）
ngrok config add-authtoken YOUR_AUTH_TOKEN
```

### 2. サーバーの起動

#### 方法A: バッチファイルを使用（推奨）
```bash
start_with_ngrok.bat
```

#### 方法B: 手動で起動
1. ターミナル1: Flaskサーバーを起動
   ```bash
   python server.py
   ```

2. ターミナル2: ngrokを起動
   ```bash
   ngrok http 5000
   ```

### 3. ngrokのURLを確認

ngrokを起動すると、以下のような画面が表示されます：

```
Forwarding  https://xxxx-xxxx-xxxx.ngrok-free.app -> http://localhost:5000
```

この `https://xxxx-xxxx-xxxx.ngrok-free.app` が外部公開URLです。

### 4. 環境変数を設定

PowerShellで環境変数を設定します：

```powershell
$env:BASE_URL="https://xxxx-xxxx-xxxx.ngrok-free.app"
python server.py
```

または、ngrokのURLが変わるたびに手動で設定する代わりに、自動的にngrokのURLを取得する方法もあります（下記参照）。

## 方法2: Cloudflare Tunnelを使用（より安定・無料）

1. Cloudflareアカウントを作成
2. cloudflaredをインストール
3. トンネルを作成して起動

詳細: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/

## 方法3: クラウドサービスにデプロイ

- Railway: https://railway.app
- Render: https://render.com
- Heroku: https://www.heroku.com

## セキュリティ対策

現在の実装では以下のセキュリティ対策が含まれています：

1. ✅ user_idの検証（/registerと/submitで必須）
2. ✅ LINE Botの署名検証（/callbackエンドポイント）
3. ✅ HTTPS対応（ngrok使用時）
4. ✅ 入力値の検証（フォームの必須項目）

### 追加推奨事項

1. **環境変数で機密情報を管理**
   - LINE Botのトークンなどを環境変数に移動

2. **レート制限の追加**
   - Flask-Limiterを使用してアクセス制限

3. **ログの監視**
   - 異常なアクセスを検知

## トラブルシューティング

### ngrokのURLが変わる問題

無料プランのngrokは、毎回起動時にURLが変わります。固定URLが必要な場合は：

1. ngrokの有料プランを使用
2. Cloudflare Tunnelを使用
3. クラウドサービスにデプロイ

### ファイアウォールの警告

Windowsファイアウォールでポート5000へのアクセス許可を求められた場合は「許可」を選択してください。

