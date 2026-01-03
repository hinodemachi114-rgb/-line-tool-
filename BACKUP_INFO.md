# バックアップ機能について

## 自動バックアップ機能

### 実装内容

✅ **自動バックアップ機能を実装しました**

1. **CSV保存時の自動バックアップ**
   - フォーム送信でCSVファイルが更新される際、自動的にバックアップを作成
   - バックアップファイル名: `members_backup_YYYYMMDD_HHMMSS.csv`

2. **サーバー起動時のバックアップ**
   - サーバー起動時に既存のCSVファイルがあればバックアップを作成

3. **バックアップファイルの管理**
   - 最大30個のバックアップを保持
   - 30個を超える場合、古いバックアップを自動削除

4. **バックアップディレクトリ**
   - バックアップは `backups/` ディレクトリに保存されます
   - ディレクトリは自動的に作成されます

### バックアップの確認方法

#### バックアップファイルの一覧を表示

**PowerShell:**
```powershell
Get-ChildItem backups\members_backup_*.csv | Sort-Object LastWriteTime -Descending
```

**CMD:**
```cmd
dir /b /o-d backups\members_backup_*.csv
```

#### 最新のバックアップを確認

**PowerShell:**
```powershell
Get-ChildItem backups\members_backup_*.csv | Sort-Object LastWriteTime -Descending | Select-Object -First 1
```

### 手動バックアップ

手動でバックアップを作成する場合：

```bash
backup_members.bat
```

または、PowerShellで：

```powershell
.\backup_members.bat
```

### バックアップからの復元

バックアップから復元する場合：

1. `backups/` ディレクトリから復元したいバックアップファイルを選択
2. そのファイルを `members.csv` にコピー

**PowerShell:**
```powershell
Copy-Item "backups\members_backup_20250103_143000.csv" "members.csv"
```

**CMD:**
```cmd
copy backups\members_backup_20250103_143000.csv members.csv
```

### バックアップの設定変更

`server.py` の以下の行で最大バックアップ数を変更できます：

```python
MAX_BACKUPS = 30  # 最大30個のバックアップを保持
```

### 注意事項

⚠️ **バックアップファイルも重要なデータです**
- バックアップディレクトリも定期的に別の場所にコピーしてください
- クラウドストレージ（Google Drive、OneDriveなど）へのバックアップを推奨

⚠️ **本番環境でのバックアップ**
- 本番環境では、外部ストレージ（AWS S3、Google Cloud Storageなど）への自動バックアップを検討してください


