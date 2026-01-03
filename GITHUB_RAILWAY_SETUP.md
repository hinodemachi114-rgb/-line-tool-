# GitHubとRailwayの連携設定

## 現在の状況

GitHubのRailway App設定画面で、リポジトリアクセスの設定を行っています。

## 次のステップ

### ステップ1: リポジトリを選択

現在「Only select repositories」が選択されています。

1. **リポジトリの選択**
   - このLINE Botプロジェクトのリポジトリを選択
   - リポジトリ名を探してチェックを入れる
   - 例: `line-tool` や `line_bot` など

2. **「Save」または「Install」ボタンをクリック**

### ステップ2: Railwayに戻る

1. Railwayのダッシュボードに戻る
2. 「New Project」を再度開く
3. 今度は接続したGitHubリポジトリが表示されるはずです

### ステップ3: リポジトリを選択してデプロイ

1. 接続したリポジトリを選択
2. 「Deploy」をクリック
3. Railwayが自動的にデプロイを開始します

## リポジトリがまだGitHubにない場合

### GitHubリポジトリを作成する手順

1. **GitHubにログイン**
   - https://github.com にアクセス

2. **新しいリポジトリを作成**
   - 「New repository」をクリック
   - リポジトリ名を入力（例: `line-tool`）
   - 「Public」または「Private」を選択
   - 「Create repository」をクリック

3. **コードをプッシュ**
   
   **初回の場合（Gitリポジトリがない場合）:**
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
   git remote add origin https://github.com/your-username/line-tool.git
   git push -u origin main
   ```

4. **Railway Appの設定に戻る**
   - GitHubの設定画面でリポジトリを選択
   - 「Save」をクリック

## 注意事項

⚠️ **リポジトリの選択**
- LINE Botプロジェクトのリポジトリを選択してください
- 複数のリポジトリがある場合は、正しいリポジトリを選択

⚠️ **権限について**
- Railway Appには以下の権限が付与されます：
  - メタデータの読み取り
  - リポジトリへの読み書きアクセス
  - これらはデプロイに必要な権限です

## 次のステップ

リポジトリを選択して「Save」をクリックした後：

1. Railwayのダッシュボードに戻る
2. プロジェクトを作成
3. 環境変数を設定
4. デプロイを開始

詳細は `RAILWAY_DEPLOY_STEPS.md` を参照してください。


