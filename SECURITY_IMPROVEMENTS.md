# セキュリティ改善内容

## 実装したセキュリティ対策

### 1. ✅ 機密情報の環境変数管理
- LINE Botのトークンとシークレットを環境変数から取得
- コードに直接書かれていた機密情報を分離
- 環境変数の設定方法:
  ```powershell
  $env:LINE_CHANNEL_ACCESS_TOKEN="your_token"
  $env:LINE_CHANNEL_SECRET="your_secret"
  ```

### 2. ✅ ログからの機密情報除外
- user_idをマスクしてログ出力（最初の8文字と最後の4文字のみ表示）
- 個人情報（氏名など）をマスクしてログ出力
- `log_safe()`関数で安全なログ出力

### 3. ✅ 入力値の検証とサニタイズ
- XSS対策: HTMLエスケープ処理
- SQLインジェクション対策: pandasを使用（SQLを使用しない）
- メールアドレスの形式検証
- 電話番号の形式検証（数字のみ、10-11桁）
- 必須項目の検証

### 4. ✅ CSRF対策
- セッションにCSRFトークンを保存
- フォーム送信時にCSRFトークンを検証
- トークン不一致の場合は403エラー

### 5. ✅ レート制限
- Flask-Limiterを使用
- `/register`: 10回/分
- `/submit`: 5回/分
- 全体: 200回/日、50回/時

### 6. ✅ user_idの形式検証
- LINEのuser_id形式を検証（Uで始まる33文字の16進数）
- 不正な形式の場合は400エラー

### 7. ✅ セキュリティヘッダー
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- X-XSS-Protection: 1; mode=block
- Strict-Transport-Security: HSTS有効
- Content-Security-Policy: CSP設定

### 8. ✅ セッション管理
- セッションにuser_idとCSRFトークンを保存
- フォーム送信後にセッションをクリア
- セッションのuser_idと送信されたuser_idを照合

## セキュリティチェックリスト

- [x] 機密情報の環境変数管理
- [x] ログからの機密情報除外
- [x] 入力値の検証とサニタイズ
- [x] CSRF対策
- [x] レート制限
- [x] user_idの形式検証
- [x] セキュリティヘッダー
- [x] セッション管理
- [x] HTTPS接続（ngrok使用時）
- [x] LINE Botの署名検証

## 追加の推奨事項

### 本番環境での設定

1. **環境変数の設定**
   ```powershell
   $env:LINE_CHANNEL_ACCESS_TOKEN="your_token"
   $env:LINE_CHANNEL_SECRET="your_secret"
   $env:FLASK_SECRET_KEY="your_secret_key"
   $env:BASE_URL="https://your-domain.com"
   ```

2. **CSVファイルの保護**
   - CSVファイルをWebサーバーの公開ディレクトリ外に配置
   - ファイルのアクセス権限を制限
   - 定期的なバックアップ

3. **ログの監視**
   - 異常なアクセスパターンを検知
   - レート制限に達したアクセスの監視
   - エラーログの定期的な確認

4. **定期的な更新**
   - 依存パッケージの更新
   - セキュリティパッチの適用

## 注意事項

⚠️ **現在の実装では、CSVファイルが同じディレクトリに保存されています。**
本番環境では、CSVファイルを安全な場所に配置し、適切なアクセス制御を設定してください。

⚠️ **環境変数が設定されていない場合、デフォルト値が使用されます。**
本番環境では必ず環境変数を設定してください。

