# Webhook 404エラーの解決方法

## エラーの内容

```
ボットサーバーから200以外のHTTPステータスコードが返されました。(404 Not Found)
```

## 原因の確認

### 1. Webhook URLが正しいか確認

LINE Developersで設定したWebhook URLを確認：

**正しいURL:**
```
https://line-tool.onrender.com/callback
```

**間違ったURL（404エラーの原因）:**
```
https://line-tool.onrender.com
```
（`/callback`が含まれていない）

### 2. Renderのサービスが起動しているか確認

1. **Renderのダッシュボードを開く**
2. **サービスをクリック**
3. **「Logs」タブを確認**
   - 「Running on http://0.0.0.0:5000」が表示されているか
   - エラーメッセージがないか

4. **サービスのステータスを確認**
   - ステータスが「Live」になっているか
   - 「Sleeping」の場合は、アクセスすると自動的に起動します

### 3. 環境変数が設定されているか確認

Renderの「Environment」タブで以下が設定されているか確認：

- `LINE_CHANNEL_ACCESS_TOKEN`
- `LINE_CHANNEL_SECRET`
- `FLASK_SECRET_KEY`
- `PORT` (5000)
- `BASE_URL` (https://line-tool.onrender.com)

## 解決方法

### ステップ1: Webhook URLを確認・修正

1. **LINE Developersコンソールを開く**
2. **「Messaging API」タブを開く**
3. **Webhook URLを確認**
   - 正しいURL: `https://line-tool.onrender.com/callback`
   - `/callback`が含まれていることを確認

4. **間違っている場合は修正**
   - Webhook URL欄に `https://line-tool.onrender.com/callback` を入力
   - 「検証」ボタンをクリック

### ステップ2: Renderのサービスを確認

1. **Renderのダッシュボードでサービスを開く**
2. **「Logs」タブを確認**
   - サーバーが起動しているか確認
   - エラーメッセージがないか確認

3. **サービスがスリープしている場合**
   - ブラウザで `https://line-tool.onrender.com` にアクセス
   - サービスが起動するまで数秒待つ
   - 再度「検証」ボタンをクリック

### ステップ3: 環境変数を確認

1. **「Environment」タブを開く**
2. **必要な環境変数がすべて設定されているか確認**
3. **設定されていない場合は追加**

### ステップ4: サービスを再起動

1. **「Manual Deploy」→「Deploy latest commit」をクリック**
2. **デプロイが完了するまで待つ**
3. **再度「検証」ボタンをクリック**

## よくある問題

### 問題1: `/callback`が含まれていない

**症状**: 404エラー

**解決方法**: Webhook URLに `/callback` を追加

### 問題2: サービスがスリープしている

**症状**: 初回アクセス時に404エラー

**解決方法**: 
1. ブラウザでサービスURLにアクセスして起動
2. 数秒待ってから再度検証

### 問題3: 環境変数が設定されていない

**症状**: サーバーが起動しない、またはエラー

**解決方法**: 必要な環境変数をすべて設定

## 確認チェックリスト

- [ ] Webhook URLに `/callback` が含まれている
- [ ] Renderのサービスが「Live」状態
- [ ] ログに「Running on http://0.0.0.0:5000」が表示されている
- [ ] 必要な環境変数がすべて設定されている
- [ ] サービスがスリープしていない（または起動済み）

## 次のステップ

すべて確認できたら、再度「検証」ボタンをクリックしてください。

成功すると「成功」と表示されます。

