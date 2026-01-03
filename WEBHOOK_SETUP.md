# Webhook URL設定手順

## ngrok URLの設定

提供されたngrok URL:
```
https://superprecise-devouringly-jairo.ngrok-free.dev
```

## ステップ1: 環境変数の設定

### 方法A: バッチファイルを使用（推奨）
```bash
set_ngrok_url.bat
```

### 方法B: PowerShellで手動設定
```powershell
$env:BASE_URL="https://superprecise-devouringly-jairo.ngrok-free.dev"
python server.py
```

### 方法C: CMDで手動設定
```cmd
set BASE_URL=https://superprecise-devouringly-jairo.ngrok-free.dev
python server.py
```

## ステップ2: LINE DevelopersでWebhook URLを設定

1. **LINE Developersコンソールにログイン**
   - https://developers.line.biz/console/

2. **チャネルを選択**

3. **「Messaging API」タブを開く**

4. **Webhook URLを設定**
   - Webhook URL欄に以下を入力:
     ```
     https://superprecise-devouringly-jairo.ngrok-free.dev/callback
     ```
   - **重要**: `/callback`を忘れずに追加してください

5. **「検証」ボタンをクリック**
   - 「成功」と表示されればOK
   - エラーが出る場合は、サーバーが起動しているか確認してください

6. **「Webhookの利用」を「利用する」に設定**

7. **「検証」ボタンで再度確認**

## ステップ3: サーバーを起動

```bash
python server.py
```

または、バッチファイルを使用:
```bash
set_ngrok_url.bat
```

## ステップ4: 動作確認

1. LINE Botにメッセージを送信（例：「こんにちは」）
2. Botから会員登録フォームのリンクが返信されることを確認
3. サーバーのログで以下が表示されることを確認:
   ```
   ★Webhook受信
   ★メッセージ受信: こんにちは
   ★user_id取得成功: [user_id]
   ★返信成功！
   ```

## トラブルシューティング

### Webhook URLの検証が失敗する場合

1. **サーバーが起動しているか確認**
   ```bash
   python server.py
   ```

2. **ngrokが起動しているか確認**
   - ngrokの画面でURLが表示されているか確認
   - 別のターミナルで `ngrok http 5000` を実行

3. **ファイアウォールの確認**
   - ポート5000がブロックされていないか確認

4. **URLの確認**
   - Webhook URLに `/callback` が含まれているか確認
   - URLにスペースや改行が入っていないか確認

### メッセージが返信されない場合

1. **サーバーのログを確認**
   - `★Webhook受信` が表示されているか
   - `★handle_message関数が呼び出されました` が表示されているか
   - エラーメッセージがないか

2. **LINE Developersの設定を確認**
   - Webhookの利用が「利用する」になっているか
   - Webhook URLが正しく設定されているか

3. **アクセストークンの確認**
   - チャネルアクセストークンが正しいか
   - トークンが有効期限内か

## 注意事項

⚠️ **ngrokの無料プランについて:**
- ngrokの無料プランでは、サーバーを再起動するたびにURLが変わる可能性があります
- URLが変わった場合は、環境変数とLINE DevelopersのWebhook URLを更新してください
- 固定URLが必要な場合は、ngrokの有料プランを使用するか、クラウドサービスにデプロイしてください

