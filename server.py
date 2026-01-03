from flask import Flask, request, abort, render_template_string, session
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import pandas as pd
import os
import socket
import re
import secrets
import html
from datetime import datetime
import shutil

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', secrets.token_hex(32))

# レート制限の設定
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# ==========================================
# 機密情報は環境変数から取得（セキュリティ強化）
# ==========================================
# 環境変数から取得、なければデフォルト値（本番環境では必ず環境変数を設定）
YOUR_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', 
    "aT+8QomDrX8euJP22yke1M1pgBD8ER/IpmWtZhna92w3buRdO8m7/WQJ8tY7nFPzupizDeSimrzpOg8gBGbfbaP2fb1QarvdlaDqxOUcOHta2G9wfVrwklDDeykafUr4k6+WbGdV9yrYAg9S0e/0EgdB04t89/1O/w1cDnyilFU=")

YOUR_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET',
    "49711c0305792eaca4262cc61f4e7868")

if not YOUR_CHANNEL_ACCESS_TOKEN or not YOUR_CHANNEL_SECRET:
    print("⚠️ 警告: LINE Botの認証情報が環境変数から取得できませんでした。")

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

CSV_FILE = 'members.csv'
EVENTS_FILE = 'events.csv'
BACKUP_DIR = 'backups'
MAX_BACKUPS = 30  # 最大30個のバックアップを保持

# バックアップディレクトリの作成
if not os.path.exists(BACKUP_DIR):
    os.makedirs(BACKUP_DIR)

# セキュリティ関数
def sanitize_input(text):
    """入力値をサニタイズ（XSS対策）"""
    if not text:
        return ''
    # HTMLエスケープ
    text = html.escape(str(text))
    # 改行とタブを許可（表示用）
    text = text.replace('&lt;br&gt;', '<br>').replace('&lt;br/&gt;', '<br>')
    return text.strip()

def validate_line_user_id(user_id):
    """LINEのuser_idの形式を検証"""
    if not user_id:
        return False
    # LINEのuser_idは通常、Uで始まる33文字の文字列
    # ただし、より柔軟に対応するため、Uで始まる32文字以上の文字列も許可
    if len(user_id) < 32:
        return False
    if not user_id.startswith('U'):
        return False
    # 英数字のみか確認
    pattern = r'^U[a-zA-Z0-9]{31,}$'
    return bool(re.match(pattern, user_id))

def validate_email(email):
    """メールアドレスの形式を検証"""
    if not email:
        return True  # 空の場合はOK（任意項目の場合）
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone):
    """電話番号の形式を検証（数字のみ、10-11桁）"""
    if not phone:
        return True  # 空の場合はOK（任意項目の場合）
    # 数字のみ、10-11桁
    pattern = r'^\d{10,11}$'
    return bool(re.match(pattern, phone))

def log_safe(message, user_id=None, sensitive_data=None):
    """機密情報を除外したログ出力"""
    if user_id:
        # user_idの一部のみ表示（最初の8文字と最後の4文字）
        masked_id = f"{user_id[:8]}...{user_id[-4:]}" if len(user_id) > 12 else "***"
        message = message.replace(user_id, masked_id)
    if sensitive_data:
        # 機密データをマスク
        for key, value in sensitive_data.items():
            if value and len(str(value)) > 4:
                masked = f"{str(value)[:2]}***{str(value)[-2:]}"
                message = message.replace(str(value), masked)
    print(message)

def backup_csv():
    """CSVファイルの自動バックアップ"""
    try:
        if not os.path.exists(CSV_FILE):
            return
        
        # バックアップファイル名（日時付き）
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'members_backup_{timestamp}.csv'
        backup_path = os.path.join(BACKUP_DIR, backup_filename)
        
        # バックアップの実行
        shutil.copy2(CSV_FILE, backup_path)
        log_safe(f"★バックアップ作成: {backup_filename}")
        
        # 古いバックアップの削除（MAX_BACKUPSを超える場合）
        backup_files = sorted([f for f in os.listdir(BACKUP_DIR) if f.startswith('members_backup_') and f.endswith('.csv')])
        if len(backup_files) > MAX_BACKUPS:
            # 古いファイルを削除
            files_to_delete = backup_files[:-MAX_BACKUPS]
            for file in files_to_delete:
                os.remove(os.path.join(BACKUP_DIR, file))
                log_safe(f"★古いバックアップ削除: {file}")
        
    except Exception as e:
        log_safe(f"★バックアップエラー: {e}")

# ベースURLの設定（環境変数から取得、なければ自動検出）
def get_base_url():
    # 環境変数にBASE_URLが設定されている場合はそれを使用
    base_url = os.getenv('BASE_URL')
    if base_url:
        return base_url.rstrip('/')
    
    # 環境変数がない場合は、PCのIPアドレスを取得
    try:
        # 外部接続用のIPアドレスを取得
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
        s.close()
        return f"http://{ip_address}:5000"
    except Exception:
        # IPアドレス取得に失敗した場合はデフォルト値
        return "http://127.0.0.1:5000"

BASE_URL = get_base_url()

# セキュリティヘッダーの設定
@app.after_request
def set_security_headers(response):
    """セキュリティヘッダーを追加"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' https://stackpath.bootstrapcdn.com; style-src 'self' 'unsafe-inline' https://stackpath.bootstrapcdn.com;"
    return response

# フォームのHTML
FORM_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>薬剤師会 会員登録</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css">
    <style>
        body { padding: 20px; background-color: #f8f9fa; }
        .container { max-width: 500px; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        h2 { text-align: center; color: #00B900; margin-bottom: 20px; font-weight: bold; }
        .btn-primary { background-color: #00B900; border-color: #00B900; width: 100%; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <h2>会員登録および変更登録</h2>
        <div class="alert alert-info" style="margin-bottom: 20px; font-size: 14px;">
            <strong>ご注意：</strong>既に登録済みの場合は、入力した内容で上書きされます。
        </div>
        <form action="/submit" method="post">
            <input type="hidden" name="user_id" value="{{ user_id }}">
            <input type="hidden" name="csrf_token" value="{{ csrf_token }}">
            <div class="form-group">
                <label>氏名（漢字）<span class="text-danger">*</span></label>
                <input type="text" name="name_kanji" class="form-control" required placeholder="例：山田 太郎">
                <small class="form-text text-muted">（名字と名前の間は半角スペースを空ける）</small>
            </div>
            <div class="form-group">
                <label>氏名（ふりがな）<span class="text-danger">*</span></label>
                <input type="text" name="name_kana" class="form-control" required placeholder="例：やまだ たろう">
                <small class="form-text text-muted">（名字と名前の間は半角スペースを空ける）</small>
            </div>
            <div class="form-group">
                <label>メールアドレス<span class="text-danger">*</span></label>
                <input type="email" name="email" class="form-control" required>
            </div>
            <div class="form-group">
                <label>電話番号<span class="text-danger">*</span></label>
                <input type="tel" name="phone" class="form-control" required placeholder="例：09012345678">
                <small class="form-text text-muted">（ハイフンを入れない）</small>
            </div>
            <div class="form-group">
                <label>所属支部<span class="text-danger">*</span></label>
                <select name="branch" class="form-control" required>
                    <option value="" disabled selected>選択してください</option>
                    <option value="博多支部">博多支部</option>
                    <option value="東支部">東支部</option>
                    <option value="中央支部">中央支部</option>
                    <option value="早良支部">早良支部</option>
                    <option value="城南支部">城南支部</option>
                    <option value="西支部">西支部</option>
                    <option value="南支部">南支部</option>
                    <option value="病院勤務">病院勤務</option>
                </select>
            </div>
            <div class="form-group">
                <label>会員情報<span class="text-danger">*</span></label>
                <select name="member_type" class="form-control" required>
                    <option value="" disabled selected>選択してください</option>
                    <option value="A会員">A会員</option>
                    <option value="B会員">B会員</option>
                    <option value="学生会員">学生会員</option>
                </select>
            </div>
            <div class="form-group">
                <label>配信希望情報<span class="text-danger">*</span></label>
                <select name="delivery_preference" class="form-control" required>
                    <option value="" disabled selected>選択してください</option>
                    <option value="学生向け">学生向け</option>
                    <option value="イベント・研修会情報のみ">イベント・研修会情報のみ</option>
                    <option value="すべての情報">すべての情報</option>
                </select>
            </div>
            <div class="form-group">
                <label>勤務先・大学名<span class="text-danger">*</span></label>
                <input type="text" name="company" class="form-control" required>
            </div>
            <button type="submit" class="btn btn-primary mt-3">登 録 す る</button>
        </form>
    </div>
</body>
</html>
"""

SUCCESS_HTML = """
<!DOCTYPE html>
<html>
<body class="text-center" style="padding: 50px;">
    <h1 style="color: #00B900;">✔ 登録完了</h1>
    <p>ありがとうございます。画面を閉じてLINEに戻ってください。</p>
</body>
</html>
"""

def init_csv():
    if not os.path.exists(CSV_FILE):
        df = pd.DataFrame(columns=['id', '氏名(漢字)', '氏名(ふりがな)', 'メールアドレス', '連絡先', '電話番号', '支部', '会員情報', '配信希望情報', '勤務先・大学名'])
        df.to_csv(CSV_FILE, index=False, encoding='utf-8-sig')

def init_events_csv():
    """イベント情報のCSVファイルを初期化"""
    if not os.path.exists(EVENTS_FILE):
        df = pd.DataFrame(columns=['id', 'イベント名', '日時', '場所', '詳細URL', '説明', '作成日時'])
        df.to_csv(EVENTS_FILE, index=False, encoding='utf-8-sig')

@app.route("/callback", methods=['GET', 'POST'])
def callback():
    # GETリクエストの場合は200を返す（LINEの検証用）
    if request.method == 'GET':
        return 'OK', 200
    
    # POSTリクエストの処理
    # リクエストの詳細をログ出力
    print("=" * 60)
    print("★Webhook受信")
    print(f"★リクエストメソッド: {request.method}")
    print(f"★リクエストヘッダー: {dict(request.headers)}")
    
    signature = request.headers.get('X-Line-Signature', '')
    if not signature:
        print("★エラー: X-Line-Signatureヘッダーが見つかりません")
        abort(400)
    
    body = request.get_data(as_text=True)
    print(f"★リクエストボディの長さ: {len(body)}文字")
    
    try:
        handler.handle(body, signature)
        print("★Webhook処理成功")
    except InvalidSignatureError as e:
        print("=" * 60)
        print("★エラー：署名検証に失敗しました。シークレットが間違っている可能性があります。")
        print(f"★エラー詳細: {e}")
        print("=" * 60)
        abort(400)
    except Exception as e:
        print("=" * 60)
        print(f"★Webhook処理エラー: {e}")
        import traceback
        traceback.print_exc()
        print("=" * 60)
        abort(500)
    
    print("=" * 60)
    return 'OK'

@app.route("/register")
@limiter.limit("10 per minute")
def register():
    try:
        user_id = request.args.get('user_id', '').strip()
        print(f"★フォームアクセス - user_id: {user_id[:8]}...{user_id[-4:] if len(user_id) > 12 else '***'}")
        
        # user_idが空の場合はエラー
        if not user_id:
            print("★エラー: user_idが空です")
            return render_template_string("""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>エラー</title>
            </head>
            <body style="padding: 50px; text-align: center; font-family: Arial, sans-serif;">
                <h2 style="color: #d32f2f;">エラー</h2>
                <p>user_idパラメータが必要です。</p>
                <p>LINE Botから送られたリンクを使用してください。</p>
                <p><a href="/">トップページに戻る</a></p>
            </body>
            </html>
            """), 400
        
        # user_idの形式を検証（緩和版）
        if not validate_line_user_id(user_id):
            print(f"★警告: user_id形式が標準的ではありませんが、処理を続行します - user_id: {user_id[:8]}...{user_id[-4:] if len(user_id) > 12 else '***'}")
            # 警告のみで処理を続行（より柔軟に対応）
        
        # セッションにuser_idを保存（CSRF対策の一部）
        # セッションが使えない環境でも動作するように、csrf_tokenを生成
        csrf_token = secrets.token_hex(16)
        try:
            session['user_id'] = user_id
            session['csrf_token'] = csrf_token
        except Exception as e:
            print(f"★セッション保存エラー（無視して続行）: {e}")
            # セッションが使えない場合は、csrf_tokenのみ使用
        
        print(f"★フォーム表示準備完了 - user_id: {user_id[:8]}...{user_id[-4:] if len(user_id) > 12 else '***'}")
        return render_template_string(FORM_HTML, user_id=user_id, csrf_token=csrf_token)
    
    except Exception as e:
        print(f"★フォーム表示エラー: {e}")
        import traceback
        traceback.print_exc()
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>エラー</title>
        </head>
        <body style="padding: 50px; text-align: center; font-family: Arial, sans-serif;">
            <h2 style="color: #d32f2f;">エラーが発生しました</h2>
            <p>フォームの表示中にエラーが発生しました。</p>
            <p>もう一度お試しください。</p>
            <p><a href="/">トップページに戻る</a></p>
        </body>
        </html>
        """), 500

@app.route("/submit", methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def submit():
    if request.method == 'GET':
        # GETアクセスの場合はフォームページにリダイレクト（user_idがあれば）
        user_id = request.args.get('user_id', '')
        if user_id:
            return render_template_string(FORM_HTML, user_id=user_id)
        else:
            return render_template_string("""
            <!DOCTYPE html>
            <html>
            <body style="padding: 50px; text-align: center;">
                <h2 style="color: #d32f2f;">エラー</h2>
                <p>このページは直接アクセスできません。</p>
                <p>LINE Botから送られたリンクを使用してください。</p>
                <p><a href="/">トップページに戻る</a></p>
            </body>
            </html>
            """)
    
    # POSTアクセスの場合（フォーム送信）
    try:
        init_csv()
        data = request.form
        user_id = data.get('user_id', '').strip()
        csrf_token = data.get('csrf_token', '').strip()
        
        # セキュリティログ（機密情報をマスク）
        log_safe("★フォーム送信受信", user_id=user_id)
        
        # CSRFトークンの検証
        if not csrf_token or csrf_token != session.get('csrf_token'):
            log_safe("★エラー: CSRFトークン検証失敗", user_id=user_id)
            abort(403, description="CSRFトークンの検証に失敗しました")
        
        # user_idの検証
        if not user_id:
            log_safe("★エラー: user_idが空です")
            return render_template_string("""
            <!DOCTYPE html>
            <html>
            <body style="padding: 50px; text-align: center;">
                <h2 style="color: #d32f2f;">エラー</h2>
                <p>user_idが取得できませんでした。</p>
                <p>LINE Botから送られたリンクを使用してください。</p>
                <p><a href="/">トップページに戻る</a></p>
            </body>
            </html>
            """)
        
        # user_idの形式を検証
        if not validate_line_user_id(user_id):
            log_safe("★エラー: 不正なuser_id形式", user_id=user_id)
            abort(400, description="不正なuser_id形式です")
        
        # セッションのuser_idと一致するか確認
        if session.get('user_id') != user_id:
            log_safe("★エラー: セッションのuser_idと一致しません", user_id=user_id)
            abort(403, description="セッションエラーが発生しました")
        
        df = pd.read_csv(CSV_FILE, encoding='utf-8-sig')
        df = df[df['id'] != user_id]
        
        # 既存のCSVに新しい列がない場合は追加
        required_columns = ['id', '氏名(漢字)', '氏名(ふりがな)', 'メールアドレス', '連絡先', '電話番号', '支部', '会員情報', '配信希望情報', '勤務先・大学名']
        for col in required_columns:
            if col not in df.columns:
                df[col] = ''
        
        # 入力値の検証とサニタイズ
        name_kanji = sanitize_input(data.get('name_kanji', ''))
        name_kana = sanitize_input(data.get('name_kana', ''))
        email = sanitize_input(data.get('email', ''))
        phone = sanitize_input(data.get('phone', ''))
        branch = sanitize_input(data.get('branch', ''))
        member_type = sanitize_input(data.get('member_type', ''))
        delivery_preference = sanitize_input(data.get('delivery_preference', ''))
        company = sanitize_input(data.get('company', ''))
        
        # 必須項目の検証
        if not name_kanji or not name_kana or not branch or not member_type or not delivery_preference or not company:
            log_safe("★エラー: 必須項目が不足しています", user_id=user_id)
            return render_template_string("""
            <!DOCTYPE html>
            <html>
            <body style="padding: 50px; text-align: center;">
                <h2 style="color: #d32f2f;">エラー</h2>
                <p>必須項目が入力されていません。</p>
                <p><a href="/register?user_id={user_id}">フォームに戻る</a></p>
            </body>
            </html>
            """.replace('{user_id}', user_id))
        
        # メールアドレスの検証
        if email and not validate_email(email):
            log_safe("★エラー: 不正なメールアドレス形式", user_id=user_id)
            return render_template_string("""
            <!DOCTYPE html>
            <html>
            <body style="padding: 50px; text-align: center;">
                <h2 style="color: #d32f2f;">エラー</h2>
                <p>メールアドレスの形式が正しくありません。</p>
                <p><a href="/register?user_id={user_id}">フォームに戻る</a></p>
            </body>
            </html>
            """.replace('{user_id}', user_id))
        
        # 電話番号の検証
        if phone and not validate_phone(phone):
            log_safe("★エラー: 不正な電話番号形式", user_id=user_id)
            return render_template_string("""
            <!DOCTYPE html>
            <html>
            <body style="padding: 50px; text-align: center;">
                <h2 style="color: #d32f2f;">エラー</h2>
                <p>電話番号は数字のみ、10-11桁で入力してください。</p>
                <p><a href="/register?user_id={user_id}">フォームに戻る</a></p>
            </body>
            </html>
            """.replace('{user_id}', user_id))
        
        new_data = {
            'id': user_id, 
            '氏名(漢字)': name_kanji, 
            '氏名(ふりがな)': name_kana,
            'メールアドレス': email, 
            '連絡先': '', 
            '電話番号': phone,
            '支部': branch, 
            '会員情報': member_type,
            '配信希望情報': delivery_preference,
            '勤務先・大学名': company
        }
        df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
        
        # 保存前にバックアップを作成
        backup_csv()
        
        df.to_csv(CSV_FILE, index=False, encoding='utf-8-sig')
        log_safe("★CSV保存完了", user_id=user_id, sensitive_data={'name': name_kanji})
        
        # セッションをクリア
        session.pop('user_id', None)
        session.pop('csrf_token', None)
        
        # LINEに通知を送信
        try:
            line_bot_api.push_message(user_id, TextSendMessage(text=f"{name_kanji} 様\n登録完了しました！\n支部: {branch}"))
            log_safe("★LINE通知送信成功", user_id=user_id)
        except Exception as e:
            log_safe(f"★エラー（LINE通知送信失敗）: {str(e)}", user_id=user_id)
        
        return render_template_string(SUCCESS_HTML)
    
    except Exception as e:
        print(f"★フォーム送信エラー: {e}")
        import traceback
        traceback.print_exc()
        user_id_for_error = ''
        try:
            user_id_for_error = request.form.get('user_id', '')
        except:
            pass
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <body style="padding: 50px; text-align: center;">
            <h2 style="color: #d32f2f;">エラーが発生しました</h2>
            <p>登録処理中にエラーが発生しました。</p>
            <p>もう一度お試しください。</p>
            <p><a href="/register?user_id={user_id}">フォームに戻る</a></p>
        </body>
        </html>
        """.replace('{user_id}', user_id_for_error))

@app.route("/profile")
@limiter.limit("10 per minute")
def profile():
    """会員情報確認ページ"""
    try:
        user_id = request.args.get('user_id', '').strip()
        
        if not user_id:
            return render_template_string("""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>エラー</title>
            </head>
            <body style="padding: 50px; text-align: center; font-family: Arial, sans-serif;">
                <h2 style="color: #d32f2f;">エラー</h2>
                <p>user_idパラメータが必要です。</p>
                <p><a href="/">トップページに戻る</a></p>
            </body>
            </html>
            """), 400
        
        # CSVから会員情報を取得
        if not os.path.exists(CSV_FILE):
            return render_template_string("""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>会員情報確認</title>
            </head>
            <body style="padding: 50px; text-align: center; font-family: Arial, sans-serif;">
                <h2>会員情報確認</h2>
                <p>会員情報が見つかりませんでした。</p>
                <p><a href="/register?user_id={user_id}">会員登録を行う</a></p>
            </body>
            </html>
            """.replace('{user_id}', user_id))
        
        df = pd.read_csv(CSV_FILE, encoding='utf-8-sig')
        member_data = df[df['id'] == user_id]
        
        if len(member_data) == 0:
            return render_template_string("""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>会員情報確認</title>
            </head>
            <body style="padding: 50px; text-align: center; font-family: Arial, sans-serif;">
                <h2>会員情報確認</h2>
                <p>会員情報が見つかりませんでした。</p>
                <p><a href="/register?user_id={user_id}">会員登録を行う</a></p>
            </body>
            </html>
            """.replace('{user_id}', user_id))
        
        member = member_data.iloc[0]
        
        # 会員情報を表示
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>会員情報確認</title>
            <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css">
            <style>
                body {{ padding: 20px; background-color: #f8f9fa; }}
                .container {{ max-width: 600px; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
                h2 {{ text-align: center; color: #00B900; margin-bottom: 30px; }}
                .info-row {{ padding: 15px; border-bottom: 1px solid #eee; }}
                .info-label {{ font-weight: bold; color: #666; }}
                .info-value {{ color: #333; }}
                .btn-primary {{ background-color: #00B900; border-color: #00B900; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>会員情報確認</h2>
                <div class="info-row">
                    <div class="info-label">氏名（漢字）</div>
                    <div class="info-value">{html.escape(str(member.get('氏名(漢字)', '')))}</div>
                </div>
                <div class="info-row">
                    <div class="info-label">氏名（ふりがな）</div>
                    <div class="info-value">{html.escape(str(member.get('氏名(ふりがな)', '')))}</div>
                </div>
                <div class="info-row">
                    <div class="info-label">メールアドレス</div>
                    <div class="info-value">{html.escape(str(member.get('メールアドレス', '')))}</div>
                </div>
                <div class="info-row">
                    <div class="info-label">電話番号</div>
                    <div class="info-value">{html.escape(str(member.get('電話番号', '')))}</div>
                </div>
                <div class="info-row">
                    <div class="info-label">所属支部</div>
                    <div class="info-value">{html.escape(str(member.get('支部', '')))}</div>
                </div>
                <div class="info-row">
                    <div class="info-label">会員情報</div>
                    <div class="info-value">{html.escape(str(member.get('会員情報', '')))}</div>
                </div>
                <div class="info-row">
                    <div class="info-label">配信希望情報</div>
                    <div class="info-value">{html.escape(str(member.get('配信希望情報', '')))}</div>
                </div>
                <div class="info-row">
                    <div class="info-label">勤務先・大学名</div>
                    <div class="info-value">{html.escape(str(member.get('勤務先・大学名', '')))}</div>
                </div>
                <div style="margin-top: 30px; text-align: center;">
                    <a href="/register?user_id={user_id}" class="btn btn-primary">登録情報を変更する</a>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    except Exception as e:
        print(f"★会員情報確認エラー: {e}")
        import traceback
        traceback.print_exc()
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>エラー</title>
        </head>
        <body style="padding: 50px; text-align: center; font-family: Arial, sans-serif;">
            <h2 style="color: #d32f2f;">エラーが発生しました</h2>
            <p>会員情報の取得中にエラーが発生しました。</p>
            <p><a href="/">トップページに戻る</a></p>
        </body>
        </html>
        """), 500

@app.route("/events")
@limiter.limit("10 per minute")
def events():
    """イベント・研修会一覧ページ"""
    try:
        user_id = request.args.get('user_id', '').strip()
        
        if not user_id:
            return render_template_string("""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>エラー</title>
            </head>
            <body style="padding: 50px; text-align: center; font-family: Arial, sans-serif;">
                <h2 style="color: #d32f2f;">エラー</h2>
                <p>user_idパラメータが必要です。</p>
                <p><a href="/">トップページに戻る</a></p>
            </body>
            </html>
            """), 400
        
        init_events_csv()
        
        # イベント情報を読み込み
        if not os.path.exists(EVENTS_FILE):
            return render_template_string("""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>イベント一覧</title>
            </head>
            <body style="padding: 50px; text-align: center; font-family: Arial, sans-serif;">
                <h2>イベント・研修会一覧</h2>
                <p>現在、申し込み中のイベント・研修会はありません。</p>
                <p><a href="/profile?user_id={user_id}">会員情報に戻る</a></p>
            </body>
            </html>
            """.replace('{user_id}', user_id))
        
        df_events = pd.read_csv(EVENTS_FILE, encoding='utf-8-sig')
        
        # ユーザーが申し込んでいるイベントを取得（将来的に実装）
        # 現在はすべてのイベントを表示
        events_list = df_events.to_dict('records')
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>イベント・研修会一覧</title>
            <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css">
            <style>
                body {{ padding: 20px; background-color: #f8f9fa; }}
                .container {{ max-width: 800px; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
                h2 {{ text-align: center; color: #00B900; margin-bottom: 30px; }}
                .event-card {{ padding: 20px; margin-bottom: 20px; border: 1px solid #ddd; border-radius: 5px; }}
                .event-title {{ font-size: 18px; font-weight: bold; color: #333; margin-bottom: 10px; }}
                .event-info {{ color: #666; margin-bottom: 5px; }}
                .btn-link {{ color: #00B900; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>イベント・研修会一覧</h2>
        """
        
        if len(events_list) == 0:
            html_content += """
                <p style="text-align: center; color: #666;">現在、申し込み中のイベント・研修会はありません。</p>
            """
        else:
            for event in events_list:
                event_name = html.escape(str(event.get('イベント名', '')))
                event_date = html.escape(str(event.get('日時', '')))
                event_location = html.escape(str(event.get('場所', '')))
                event_url = html.escape(str(event.get('詳細URL', '')))
                event_desc = html.escape(str(event.get('説明', '')))
                
                html_content += f"""
                <div class="event-card">
                    <div class="event-title">{event_name}</div>
                    <div class="event-info">📅 日時: {event_date}</div>
                    <div class="event-info">📍 場所: {event_location}</div>
                    {f'<div class="event-info">{event_desc}</div>' if event_desc else ''}
                    {f'<a href="{event_url}" target="_blank" class="btn-link">詳細を見る →</a>' if event_url else ''}
                </div>
                """
        
        html_content += f"""
                <div style="margin-top: 30px; text-align: center;">
                    <a href="/profile?user_id={user_id}" class="btn btn-secondary">会員情報に戻る</a>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    except Exception as e:
        print(f"★イベント一覧エラー: {e}")
        import traceback
        traceback.print_exc()
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>エラー</title>
        </head>
        <body style="padding: 50px; text-align: center; font-family: Arial, sans-serif;">
            <h2 style="color: #d32f2f;">エラーが発生しました</h2>
            <p>イベント一覧の取得中にエラーが発生しました。</p>
            <p><a href="/">トップページに戻る</a></p>
        </body>
        </html>
        """), 500

@app.route("/")
def index():
    """ルートパス - ヘルスチェック用"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>LINE Bot 会員登録システム</title>
    </head>
    <body style="padding: 50px; text-align: center; font-family: Arial, sans-serif;">
        <h1>LINE Bot 会員登録システム</h1>
        <p>このシステムは正常に動作しています。</p>
        <p>LINE Botから送られたリンクを使用して会員登録を行ってください。</p>
        <hr>
        <p><small>Status: OK | BASE_URL: """ + BASE_URL + """</small></p>
    </body>
    </html>
    """, 200

@app.errorhandler(404)
def not_found(error):
    """404エラーハンドラー"""
    print(f"★404エラー: {request.url}")
    print(f"★リクエストパス: {request.path}")
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>404 Not Found</title>
    </head>
    <body style="padding: 50px; text-align: center; font-family: Arial, sans-serif;">
        <h2 style="color: #d32f2f;">404 Not Found</h2>
        <p>リクエストされたページが見つかりませんでした。</p>
        <p>リクエストパス: """ + request.path + """</p>
        <p>BASE_URL: """ + BASE_URL + """</p>
        <p><a href="/">トップページに戻る</a></p>
    </body>
    </html>
    """), 404

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print("-" * 60)
    print("★handle_message関数が呼び出されました")
    
    try:
        user_message = event.message.text
        print(f"★メッセージ受信: {user_message}")
        
        # user_idの取得を試行
        user_id = None
        try:
            if hasattr(event.source, 'user_id'):
                user_id = event.source.user_id
            elif hasattr(event, 'source') and hasattr(event.source, 'user_id'):
                user_id = event.source.user_id
            else:
                # 直接アクセスを試行
                user_id = getattr(event.source, 'user_id', None)
        except Exception as e:
            print(f"★user_id取得エラー: {e}")
        
        if not user_id:
            print("★警告: user_idが取得できませんでした")
            print(f"★event.sourceの型: {type(event.source)}")
            print(f"★event.sourceの属性: {dir(event.source)}")
            # 代替方法を試行
            if hasattr(event.source, 'type'):
                print(f"★event.source.type: {event.source.type}")
            
            # user_idが取得できない場合でも、エラーメッセージを送信
            try:
                error_msg = "申し訳ございません。システムエラーが発生しました。しばらくしてから再度お試しください。"
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=error_msg))
                print("★エラーメッセージを送信しました")
            except Exception as e:
                print(f"★エラーメッセージ送信失敗: {e}")
            return
        
        # 既に登録済みかチェック
        is_registered = False
        try:
            if os.path.exists(CSV_FILE):
                df = pd.read_csv(CSV_FILE, encoding='utf-8-sig')
                if 'id' in df.columns:
                    is_registered = user_id in df['id'].values
                    log_safe(f"★登録状況: {'登録済み' if is_registered else '未登録'}", user_id=user_id)
        except Exception as e:
            log_safe(f"★登録状況確認エラー: {e}", user_id=user_id)
        
        # BASE_URLを使用してURLを生成（環境変数やIPアドレスを使用）
        form_url = f"{BASE_URL}/register?user_id={user_id}"
        log_safe("★フォームURL生成完了", user_id=user_id)
        
        # 挨拶に応答するメッセージを作成
        greeting_responses = {
            'こんにちは': 'こんにちは！',
            'こんばんは': 'こんばんは！',
            'おはよう': 'おはようございます！',
            'ありがとう': 'どういたしまして！',
            'よろしく': 'よろしくお願いします！'
        }
        
        # 挨拶チェック（部分一致）
        greeting = None
        user_message_lower = user_message.lower()
        for key in greeting_responses:
            if key in user_message or key in user_message_lower:
                greeting = greeting_responses[key]
                break
        
        # メッセージを構築
        if is_registered:
            if greeting:
                msg = f"{greeting}\n\n会員登録ありがとうございます！\n\n既に登録済みですが、情報を変更する場合は以下のリンクからお願いします。\n\n🔻 会員情報変更フォーム\n{form_url}"
            else:
                msg = f"会員登録ありがとうございます！\n\n既に登録済みですが、情報を変更する場合は以下のリンクからお願いします。\n\n🔻 会員情報変更フォーム\n{form_url}"
        else:
            if greeting:
                msg = f"{greeting}\n\n薬剤師会の会員登録をお願いします！\n\n以下のリンクから会員情報を入力してください。\n\n🔻 会員登録フォーム\n{form_url}"
            else:
                msg = f"こんにちは！\n\n薬剤師会の会員登録をお願いします！\n\n以下のリンクから会員情報を入力してください。\n\n🔻 会員登録フォーム\n{form_url}"
        
            log_safe(f"★送信メッセージ準備完了", user_id=user_id)
        
        try:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=msg))
            log_safe(f"★返信成功！登録済み: {is_registered}", user_id=user_id)
        except LineBotApiError as e:
            print("=" * 60)
            print("★返信エラー発生！アクセストークンが間違っている可能性が高いです。")
            print(f"★エラー詳細: {e}")
            print(f"★エラーステータス: {e.status_code}")
            print(f"★エラーレスポンス: {e.error}")
            print("=" * 60)
        except Exception as e:
            print(f"★予期せぬエラー: {e}")
            import traceback
            traceback.print_exc()
        
        print("-" * 60)
    except Exception as e:
        print("=" * 60)
        print(f"★handle_messageでエラー発生: {e}")
        import traceback
        traceback.print_exc()
        print("=" * 60)

# サーバー起動時に既存のCSVファイルがあればバックアップ
if os.path.exists(CSV_FILE):
    try:
        backup_csv()
    except Exception as e:
        print(f"★起動時バックアップエラー: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("サーバーを起動しています...")
    print(f"ベースURL: {BASE_URL}")
    print(f"フォームURL: {BASE_URL}/register")
    print("=" * 60)
    
    if BASE_URL.startswith("http://127.0.0.1") or BASE_URL.startswith("http://192.168") or BASE_URL.startswith("http://10."):
        print("\n⚠️  ローカルネットワーク用のURLです")
        print("外部公開する場合は、環境変数BASE_URLを設定してください:")
        print("  PowerShell: $env:BASE_URL=\"https://your-ngrok-url.ngrok.io\"")
        print("  CMD: set BASE_URL=https://your-ngrok-url.ngrok.io")
    else:
        print("\n✓ 外部公開URLが設定されています")
    
    print("\nフォームのアクセスURL:")
    print(f"  → {BASE_URL}/register?user_id=YOUR_USER_ID")
    print("\nセキュリティ:")
    print("  ✓ user_idの検証が有効")
    print("  ✓ LINE Botの署名検証が有効")
    if BASE_URL.startswith("https://"):
        print("  ✓ HTTPS接続が有効")
    print("=" * 60)
    print()
    
    # ポート番号の取得（環境変数PORTがあればそれを使用、なければ5000）
    port = int(os.getenv('PORT', 5000))
    # デバッグモードは本番環境では無効化
    debug_mode = os.getenv('FLASK_ENV', 'production') == 'development'
    
    app.run(host='0.0.0.0', port=port, debug=debug_mode)