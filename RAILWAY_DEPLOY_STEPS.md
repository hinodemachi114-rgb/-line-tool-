# Railwayデプロイ手順（ステップバイステップ）

## ステップ1: GitHubリポジトリの準備

### 1-1. GitHubリポジトリを作成

1. GitHubにログイン: https://github.com
2. 「New repository」をクリック
3. リポジトリ名を入力（例: `line-tool`）
4. 「Create repository」をクリック

### 1-2. コードをGitHubにプッシュ

**初回の場合:**
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/your-username/line-tool.git
git push -u origin main
```

**既にGitリポジトリがある場合:**
```bash
git add .
git commit -m "Prepare for Railway deployment"
git push origin main
```

## ステップ2: Railwayでプロジェクトを作成

### 2-1. Railwayにログイン

1. https://railway.app にアクセス
2. 「Start a New Project」をクリック
3. GitHubアカウントでログイン

### 2-2. リポジトリを選択

1. 「新しいプロジェクト」画面で「GitHub Repository」を選択
2. 作成したリポジトリを選択
3. 「Deploy」をクリック

## ステップ3: 環境変数の設定

### 3-1. 環境変数を追加

Railwayのダッシュボードで：

1. プロジェクトを選択
2. 「Variables」タブをクリック
3. 「New Variable」をクリック
4. 以下の環境変数を追加：

```
LINE_CHANNEL_ACCESS_TOKEN = aT+8QomDrX8euJP22yke1M1pgBD8ER/IpmWtZhna92w3buRdO8m7/WQJ8tY7nFPzupizDeSimrzpOg8gBGbfbaP2fb1QarvdlaDqxOUcOHta2G9wfVrwklDDeykafUr4k6+WbGdV9yrYAg9S0e/0EgdB04t89/1O/w1cDnyilFU=

LINE_CHANNEL_SECRET = 49711c0305792eaca4262cc61f4e7868

FLASK_SECRET_KEY = 2cd43422607bff4c43662b2b98018670281e3da677347caad4c7c1427dd43d3c

PORT = 5000
```

**重要**: `BASE_URL`は後で設定します（デプロイ後のURLを使用）

### 3-2. BASE_URLの設定

デプロイが完了したら：

1. Railwayのダッシュボードで「Settings」タブを開く
2. 「Domains」セクションでURLを確認（例: `your-app.railway.app`）
3. 環境変数に追加：
   ```
   BASE_URL = https://your-app.railway.app
   ```

## ステップ4: デプロイの確認

### 4-1. デプロイ状況の確認

1. Railwayのダッシュボードで「Deployments」タブを確認
2. デプロイが成功するまで待機（数分かかります）
3. 「View Logs」でログを確認

### 4-2. デプロイURLの確認

1. 「Settings」タブを開く
2. 「Domains」セクションでURLを確認
3. このURLが `BASE_URL` になります

## ステップ5: LINE DevelopersでWebhook URLを設定

### 5-1. Webhook URLを更新

1. LINE Developersコンソールにログイン
2. チャネルを選択
3. 「Messaging API」タブを開く
4. Webhook URLを設定:
   ```
   https://your-app.railway.app/callback
   ```
   （`your-app.railway.app`を実際のRailwayのURLに置き換え）

5. 「検証」ボタンをクリック
6. 「成功」と表示されればOK

### 5-2. Webhookの利用を有効化

「Webhookの利用」を「利用する」に設定

## ステップ6: 動作確認

1. LINE Botにメッセージを送信
2. Botから会員登録フォームのリンクが返信されることを確認
3. フォームが正常に表示されることを確認
4. フォーム送信が成功することを確認

## トラブルシューティング

### デプロイが失敗する場合

1. **ログを確認**
   - Railwayのダッシュボードで「View Logs」を確認
   - エラーメッセージを確認

2. **requirements.txtを確認**
   - すべての依存パッケージが含まれているか確認

3. **Procfileを確認**
   - `web: python server.py` が正しく設定されているか確認

### Webhook URLの検証が失敗する場合

1. **サーバーが起動しているか確認**
   - Railwayのログでサーバーが起動しているか確認

2. **URLが正しいか確認**
   - `/callback` が含まれているか確認
   - HTTPSを使用しているか確認

3. **環境変数が正しく設定されているか確認**
   - Railwayのダッシュボードで環境変数を確認

## 次のステップ

- バックアップの設定（既に実装済み）
- 監視の設定
- 定期的なメンテナンス


