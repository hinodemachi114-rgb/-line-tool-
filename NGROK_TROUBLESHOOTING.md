# ngrokエラー解決ガイド

## エラー: ERR_NGROK_3200 - エンドポイントがオフライン

このエラーは、ngrokのトンネルが起動していないか、Flaskサーバーが起動していないことを示しています。

## 解決方法

### ステップ1: Flaskサーバーを起動

**ターミナル1（Flaskサーバー用）:**
```bash
set BASE_URL=https://superprecise-devouringly-jairo.ngrok-free.dev
python server.py
```

または、バッチファイルを使用:
```bash
set_ngrok_url.bat
```

サーバーが起動すると、以下のようなメッセージが表示されます:
```
============================================================
サーバーを起動しています...
ベースURL: https://superprecise-devouringly-jairo.ngrok-free.dev
============================================================
 * Running on http://0.0.0.0:5000
```

### ステップ2: ngrokを起動

**ターミナル2（ngrok用）:**
```bash
ngrok http 5000
```

ngrokが起動すると、以下のような画面が表示されます:
```
Forwarding  https://superprecise-devouringly-jairo.ngrok-free.dev -> http://localhost:5000
```

### ステップ3: 両方を同時に起動（推奨）

**バッチファイルを使用:**
```bash
start_server_with_ngrok.bat
```

このバッチファイルは、Flaskサーバーとngrokを自動的に起動します。

## 確認事項

### 1. サーバーが起動しているか確認

ブラウザで以下のURLにアクセス:
```
http://localhost:5000
```

または:
```
http://127.0.0.1:5000
```

「会員登録および変更登録」のフォームが表示されれば、サーバーは正常に起動しています。

### 2. ngrokが起動しているか確認

ngrokの画面で以下のような表示があるか確認:
```
Session Status                online
Forwarding                    https://superprecise-devouringly-jairo.ngrok-free.dev -> http://localhost:5000
```

### 3. ポート5000が使用されているか確認

PowerShellで確認:
```powershell
netstat -ano | findstr :5000
```

何か表示されれば、ポート5000でサーバーが起動しています。

## よくある問題

### 問題1: ポート5000が既に使用されている

**解決方法:**
- 他のアプリケーションがポート5000を使用していないか確認
- サーバーを再起動
- 別のポートを使用（その場合はngrokの設定も変更）

### 問題2: ngrokのURLが変わった

**解決方法:**
1. ngrokの画面で新しいURLを確認
2. 環境変数BASE_URLを更新
3. LINE DevelopersのWebhook URLを更新

### 問題3: ファイアウォールがブロックしている

**解決方法:**
- Windowsファイアウォールでポート5000を許可
- セキュリティソフトがブロックしていないか確認

## 動作確認

1. **サーバーとngrokを起動**
2. **ブラウザでngrokのURLにアクセス**
   ```
   https://superprecise-devouringly-jairo.ngrok-free.dev
   ```
3. **フォームが表示されれば成功**
4. **LINE DevelopersでWebhook URLを設定**
   ```
   https://superprecise-devouringly-jairo.ngrok-free.dev/callback
   ```
5. **「検証」ボタンをクリックして成功を確認**

## 次のステップ

サーバーとngrokが正常に起動したら:
1. LINE DevelopersでWebhook URLを設定
2. LINE Botにメッセージを送信
3. Botから会員登録フォームのリンクが返信されることを確認

