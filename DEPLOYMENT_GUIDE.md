# 本番環境への移行ガイド

## 推奨プラットフォーム

### 1. Railway（推奨・簡単）

Railwayは最も簡単にデプロイできるプラットフォームです。

#### デプロイ手順

1. **Railwayアカウントを作成**
   - https://railway.app にアクセス
   - GitHubアカウントでサインアップ

2. **プロジェクトの作成**
   - "New Project" → "Deploy from GitHub repo"
   - このリポジトリを選択

3. **環境変数の設定**
   Railwayのダッシュボードで以下を設定：
   ```
   LINE_CHANNEL_ACCESS_TOKEN=your_token
   LINE_CHANNEL_SECRET=your_secret
   FLASK_SECRET_KEY=your_secret_key
   BASE_URL=https://your-app.railway.app
   ```

4. **デプロイ**
   - Railwayが自動的にデプロイします
   - デプロイ完了後、URLが表示されます

5. **LINE DevelopersでWebhook URLを設定**
   ```
   https://your-app.railway.app/callback
   ```

#### メリット
- ✅ 無料クレジットあり（毎月$5分）
- ✅ 自動デプロイ
- ✅ 固定URL
- ✅ HTTPS対応
- ✅ 簡単な設定

#### 料金
- **無料プラン**: 毎月$5分のクレジット（制限あり）
- **Hobbyプラン**: $5/月（本番環境推奨）
- **Proプラン**: $20/月

---

### 2. Render

#### デプロイ手順

1. **Renderアカウントを作成**
   - https://render.com にアクセス
   - GitHubアカウントでサインアップ

2. **New Web Service**
   - GitHubリポジトリを選択
   - 設定：
     - Build Command: `pip install -r requirements.txt`
     - Start Command: `python server.py`
     - Environment: Python 3

3. **環境変数の設定**
   Renderのダッシュボードで以下を設定：
   ```
   LINE_CHANNEL_ACCESS_TOKEN=your_token
   LINE_CHANNEL_SECRET=your_secret
   FLASK_SECRET_KEY=your_secret_key
   PORT=5000
   ```

4. **デプロイ**
   - Renderが自動的にデプロイします

#### メリット
- ✅ 完全無料プランあり
- ✅ 固定URL
- ✅ HTTPS対応

#### 料金
- **無料プラン**: 完全無料（15分非アクティブ後にスリープ）
- **Starterプラン**: $7/月（常時稼働）
- **Standardプラン**: $25/月

---

### 3. Heroku

#### デプロイ手順

1. **Herokuアカウントを作成**
   - https://www.heroku.com にアクセス

2. **Heroku CLIのインストール**
   ```bash
   # https://devcenter.heroku.com/articles/heroku-cli
   ```

3. **Herokuにログイン**
   ```bash
   heroku login
   ```

4. **アプリの作成**
   ```bash
   heroku create your-app-name
   ```

5. **環境変数の設定**
   ```bash
   heroku config:set LINE_CHANNEL_ACCESS_TOKEN=your_token
   heroku config:set LINE_CHANNEL_SECRET=your_secret
   heroku config:set FLASK_SECRET_KEY=your_secret_key
   heroku config:set BASE_URL=https://your-app-name.herokuapp.com
   ```

6. **デプロイ**
   ```bash
   git push heroku main
   ```

---

## デプロイ前の準備

### 1. requirements.txtの確認

現在のrequirements.txt:
```
pandas
streamlit
line-bot-sdk
flask
flask-limiter
```

### 2. Procfileの作成

既に作成済み:
```
web: python server.py
```

### 3. 環境変数の準備

デプロイ前に以下の環境変数を準備：
- `LINE_CHANNEL_ACCESS_TOKEN`
- `LINE_CHANNEL_SECRET`
- `FLASK_SECRET_KEY`（ランダムな文字列）
- `BASE_URL`（デプロイ後のURL）

### 4. CSVファイルの扱い

**重要**: 本番環境では、CSVファイルは以下のいずれかの方法で管理：

1. **データベースに移行**（推奨）
   - PostgreSQL、MySQL、SQLiteなど
   - より安全でスケーラブル

2. **外部ストレージを使用**
   - AWS S3、Google Cloud Storageなど
   - バックアップが自動化される

3. **現在のCSV方式を継続**
   - 定期的なバックアップが必要
   - ファイルのアクセス権限を制限

---

## デプロイ後の確認事項

### 1. Webhook URLの設定

LINE Developersで新しいWebhook URLを設定：
```
https://your-deployed-url.com/callback
```

### 2. 動作テスト

- LINE Botにメッセージを送信
- フォームが正常に表示されるか確認
- データが正しく保存されるか確認

### 3. バックアップの設定

本番環境でもバックアップを設定：
- 自動バックアップ機能は既に実装済み
- 外部ストレージへのバックアップを検討

### 4. 監視の設定

- サーバーの稼働状況を監視
- エラー発生時のアラート設定
- ログの確認

---

## セキュリティチェックリスト（本番環境）

- [ ] 環境変数が正しく設定されている
- [ ] HTTPS接続が有効
- [ ] セキュリティヘッダーが設定されている
- [ ] CSRF対策が有効
- [ ] レート制限が設定されている
- [ ] ログから機密情報が除外されている
- [ ] バックアップが設定されている
- [ ] Webhook URLが正しく設定されている

---

## トラブルシューティング

### デプロイが失敗する場合

1. **requirements.txtを確認**
   - すべての依存パッケージが含まれているか

2. **Procfileを確認**
   - 正しいコマンドが設定されているか

3. **ログを確認**
   - デプロイプラットフォームのログを確認

### Webhook URLの検証が失敗する場合

1. **サーバーが起動しているか確認**
2. **URLが正しいか確認**（`/callback`が含まれているか）
3. **環境変数が正しく設定されているか確認**

---

## 次のステップ

デプロイが完了したら：

1. 動作テストを実行
2. バックアップの設定を確認
3. 監視の設定
4. 定期的なメンテナンス計画

