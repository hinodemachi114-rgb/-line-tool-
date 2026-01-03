# ngrokを使った外部公開の設定方法

## ステップ1: ngrokのインストール

1. https://ngrok.com/download からngrokをダウンロード
2. ダウンロードしたzipファイルを解凍
3. `ngrok.exe`をこのフォルダ（`line_tool`）にコピー

## ステップ2: ngrokアカウント作成（推奨）

1. https://dashboard.ngrok.com/signup でアカウントを作成（無料）
2. ダッシュボードから認証トークンをコピー
3. 以下のコマンドで認証（オプション、無料プランでも使用可能）

```bash
ngrok config add-authtoken YOUR_AUTH_TOKEN
```

## ステップ3: サーバーとngrokを起動

### 方法A: バッチファイルを使用（簡単）

1. `start_with_ngrok.bat`をダブルクリック
2. Flaskサーバーとngrokが自動的に起動します
3. ngrokの画面で表示される `https://xxxx-xxxx.ngrok-free.app` のURLをコピー

### 方法B: 手動で起動

**ターミナル1: Flaskサーバーを起動**
```bash
python server.py
```

**ターミナル2: ngrokを起動**
```bash
ngrok http 5000
```

## ステップ4: 環境変数を設定

ngrokの画面に表示されたURL（例：`https://xxxx-xxxx.ngrok-free.app`）を環境変数に設定します。

**PowerShellの場合:**
```powershell
$env:BASE_URL="https://xxxx-xxxx.ngrok-free.app"
python server.py
```

**CMDの場合:**
```cmd
set BASE_URL=https://xxxx-xxxx.ngrok-free.app
python server.py
```

## ステップ5: LINE DevelopersでWebhook URLを設定

1. LINE Developersコンソールにログイン
2. あなたのチャネルを選択
3. 「Messaging API」タブを開く
4. 「Webhook URL」に以下のURLを入力:
   ```
   https://xxxx-xxxx.ngrok-free.app/callback
   ```
5. 「検証」ボタンをクリックして接続を確認
6. 「Webhookの利用」を「利用する」に設定

## 完了！

これで、どこからでもアクセスできるようになりました。

LINE Botにメッセージを送ると、ngrokのURLを含む登録フォームのリンクが送信されます。

## 注意事項

⚠️ **無料プランのngrokは、毎回起動時にURLが変わります**
- サーバーを再起動するたびに、ngrokのURLが変わります
- その都度、環境変数とLINE DevelopersのWebhook URLを更新する必要があります

💡 **固定URLが必要な場合:**
- ngrokの有料プランを使用
- Cloudflare Tunnelを使用
- クラウドサービス（Railway、Renderなど）にデプロイ

## トラブルシューティング

### ngrokが起動しない
- ngrok.exeが正しい場所にあるか確認
- ファイアウォールでngrokがブロックされていないか確認

### 接続できない
- 両方のサーバー（Flaskとngrok）が起動しているか確認
- ngrokのURLが正しく設定されているか確認
- LINE DevelopersのWebhook URLが正しいか確認

