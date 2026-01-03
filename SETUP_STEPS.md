# セットアップ手順（現在の進捗確認）

## 現在の状況

✅ 環境変数の設定（LINE_CHANNEL_ACCESS_TOKEN、LINE_CHANNEL_SECRET、BASE_URL）は完了
❌ FLASK_SECRET_KEYの設定が未完了

## 次のステップ: FLASK_SECRET_KEYを設定

### PowerShellで実行

以下のコマンドを実行して、FLASK_SECRET_KEYを設定してください：

```powershell
$env:FLASK_SECRET_KEY="2cd43422607bff4c43662b2b98018670281e3da677347caad4c7c1427dd43d3c"
```

### すべての環境変数を一度に設定（推奨）

以下のコマンドを順番に実行してください：

```powershell
$env:LINE_CHANNEL_ACCESS_TOKEN="aT+8QomDrX8euJP22yke1M1pgBD8ER/IpmWtZhna92w3buRdO8m7/WQJ8tY7nFPzupizDeSimrzpOg8gBGbfbaP2fb1QarvdlaDqxOUcOHta2G9wfVrwklDDeykafUr4k6+WbGdV9yrYAg9S0e/0EgdB04t89/1O/w1cDnyilFU="
$env:LINE_CHANNEL_SECRET="49711c0305792eaca4262cc61f4e7868"
$env:FLASK_SECRET_KEY="2cd43422607bff4c43662b2b98018670281e3da677347caad4c7c1427dd43d3c"
$env:BASE_URL="https://superprecise-devouringly-jairo.ngrok-free.dev"
```

### 環境変数の確認

設定が完了したら、以下のコマンドで確認できます：

```powershell
echo "LINE_CHANNEL_ACCESS_TOKEN: $env:LINE_CHANNEL_ACCESS_TOKEN"
echo "LINE_CHANNEL_SECRET: $env:LINE_CHANNEL_SECRET"
echo "FLASK_SECRET_KEY: $env:FLASK_SECRET_KEY"
echo "BASE_URL: $env:BASE_URL"
```

### サーバーの起動

環境変数の設定が完了したら、サーバーを起動：

```powershell
python server.py
```

## 完了チェックリスト

- [x] LINE_CHANNEL_ACCESS_TOKEN の設定
- [x] LINE_CHANNEL_SECRET の設定
- [ ] FLASK_SECRET_KEY の設定 ← **現在ここ**
- [x] BASE_URL の設定
- [ ] サーバーの起動

