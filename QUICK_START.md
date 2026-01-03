# クイックスタートガイド

## PowerShellでバッチファイルを実行する方法

PowerShellでは、現在のディレクトリにあるバッチファイルを実行する際は、`.\`を前に付ける必要があります。

### 正しい実行方法

```powershell
.\set_ngrok_url.bat
```

または

```powershell
.\start_server_with_ngrok.bat
```

## サーバー起動手順

### 方法1: バッチファイルを使用（推奨）

**PowerShellで実行:**
```powershell
.\start_server_with_ngrok.bat
```

このコマンドで以下が自動的に実行されます：
1. 環境変数BASE_URLを設定
2. Flaskサーバーを起動
3. ngrokトンネルを開始

### 方法2: 手動で起動

**ターミナル1（Flaskサーバー）:**
```powershell
$env:BASE_URL="https://superprecise-devouringly-jairo.ngrok-free.dev"
python server.py
```

**ターミナル2（ngrok）:**
```powershell
ngrok http 5000
```

### 方法3: CMDを使用

CMD（コマンドプロンプト）を使用する場合は、`.\`は不要です：

```cmd
set_ngrok_url.bat
```

または

```cmd
start_server_with_ngrok.bat
```

## 確認事項

サーバーが起動したら、以下のように表示されます：

```
============================================================
サーバーを起動しています...
ベースURL: https://superprecise-devouringly-jairo.ngrok-free.dev
フォームURL: https://superprecise-devouringly-jairo.ngrok-free.dev/register
============================================================

✓ 外部公開URLが設定されています
```

## 次のステップ

1. サーバーとngrokが起動したことを確認
2. LINE DevelopersでWebhook URLを設定:
   ```
   https://superprecise-devouringly-jairo.ngrok-free.dev/callback
   ```
3. 「検証」ボタンをクリックして成功を確認
4. LINE Botにメッセージを送信して動作確認

