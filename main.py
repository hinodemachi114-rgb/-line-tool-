import streamlit as st
import pandas as pd
from linebot import LineBotApi
from linebot.models import TextSendMessage, ImageSendMessage, TemplateSendMessage, ButtonsTemplate, URITemplateAction
from linebot.exceptions import LineBotApiError
import base64
import io
from PIL import Image

# ==========================================
# 認証情報（自分のキーに書き換えてください）
# ==========================================
CHANNEL_ACCESS_TOKEN = "aT+8QomDrX8euJP22yke1M1pgBD8ER/IpmWtZhna92w3buRdO8m7/WQJ8tY7nFPzupizDeSimrzpOg8gBGbfbaP2fb1QarvdlaDqxOUcOHta2G9wfVrwklDDeykafUr4k6+WbGdV9yrYAg9S0e/0EgdB04t89/1O/w1cDnyilFU="
CHANNEL_SECRET = "49711c0305792eaca4262cc61f4e7868"

# LINE Botの準備
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)

# ==========================================
# 画面のデザイン
# ==========================================
st.title("💊 薬剤師会 メッセージ配信ツール")

# 1. 名簿データの読み込み
try:
    df = pd.read_csv('members.csv', encoding='utf-8-sig')
    # もしカラム名が足りない場合の対策
    if '支部' not in df.columns:
        df['支部'] = '未定'
    
    # 名前の列を統一（'名前'があればそれを使い、空の場合は'氏名(漢字)'で補完）
    if '名前' not in df.columns:
        if '氏名(漢字)' in df.columns:
            df['名前'] = df['氏名(漢字)']
        else:
            df['名前'] = ''
    elif '氏名(漢字)' in df.columns:
        # '名前'列が空の場合、'氏名(漢字)'で補完
        df['名前'] = df['名前'].fillna('').astype(str)
        df.loc[df['名前'] == '', '名前'] = df.loc[df['名前'] == '', '氏名(漢字)'].fillna('')
except FileNotFoundError:
    st.error("会員データ（members.csv）が見つかりません。まずは会員登録を行ってください。")
    st.stop()
except Exception as e:
    st.error(f"データの読み込みエラー: {e}")
    st.stop()

# サイドバー：配信対象の絞り込み
st.sidebar.header("配信対象の選択")

# 配信希望情報の選択肢を作る（データから自動取得）
if '配信希望情報' not in df.columns:
    st.error("配信希望情報のデータが見つかりません。会員登録データを確認してください。")
    st.stop()

delivery_list = df['配信希望情報'].unique().tolist()
# 空の値を除外
delivery_list = [d for d in delivery_list if pd.notna(d) and str(d).strip() != '']

if len(delivery_list) == 0:
    st.error("配信希望情報のデータが見つかりません。")
    st.stop()

selected_delivery = st.sidebar.selectbox("配信希望情報を選択", delivery_list)

# 選択された配信希望情報の会員だけを抽出
df_filtered = df[df['配信希望情報'] == selected_delivery]

# 画面に配信対象を表示
st.subheader(f"📡 配信対象：{selected_delivery} ({len(df_filtered)}名)")

# 表示する列を決定
display_columns = []
if '名前' in df_filtered.columns:
    display_columns.append('名前')
elif '氏名(漢字)' in df_filtered.columns:
    display_columns.append('氏名(漢字)')
if '支部' in df_filtered.columns:
    display_columns.append('支部')
if '配信希望情報' in df_filtered.columns:
    display_columns.append('配信希望情報')

if display_columns:
    st.dataframe(df_filtered[display_columns])  # IDは隠して名前だけ表示
else:
    st.dataframe(df_filtered)
    
# 統計情報を表示
if len(df_filtered) > 0:
    st.write("**配信対象の内訳:**")
    if '支部' in df_filtered.columns:
        branch_counts = df_filtered['支部'].value_counts()
        st.write("支部別:")
        for branch, count in branch_counts.items():
            st.write(f"  - {branch}: {count}名")

# ==========================================
# メッセージ作成と送信
# ==========================================
st.write("---")
st.subheader("📩 メッセージ作成")

# 配信対象の追加フィルタリング
st.sidebar.subheader("追加フィルタリング（オプション）")

# 支部でのフィルタリング
if '支部' in df_filtered.columns:
    branch_list = ['すべて'] + df_filtered['支部'].unique().tolist()
    selected_branch = st.sidebar.selectbox("支部で絞り込み", branch_list)
    if selected_branch != 'すべて':
        df_filtered = df_filtered[df_filtered['支部'] == selected_branch]

# 会員情報でのフィルタリング
if '会員情報' in df_filtered.columns:
    member_type_list = ['すべて'] + df_filtered['会員情報'].unique().tolist()
    selected_member_type = st.sidebar.selectbox("会員情報で絞り込み", member_type_list)
    if selected_member_type != 'すべて':
        df_filtered = df_filtered[df_filtered['会員情報'] == selected_member_type]

# 配信対象の再表示
st.subheader(f"📡 配信対象：{len(df_filtered)}名")

# メッセージ入力フォーム
message_title = st.text_input("題名（タイトル）", placeholder="例：研修会のお知らせ")

message_text = st.text_area("詳細テキスト", height=200, placeholder="メッセージの詳細を入力してください")

# 画像アップロード
uploaded_image = st.file_uploader("画像をアップロード（オプション）", type=['png', 'jpg', 'jpeg'], help="最大1MBまで")

# リンクURL
link_url = st.text_input("リンクURL（オプション）", placeholder="例：https://forms.gle/... または詳細ページのURL")

# プレビュー表示
if message_title or message_text:
    st.subheader("📋 プレビュー")
    if message_title:
        st.write(f"**{message_title}**")
    if message_text:
        st.write(message_text)
    if uploaded_image:
        st.image(uploaded_image, caption="アップロードされた画像", use_container_width=True)
    if link_url:
        st.write(f"🔗 リンク: {link_url}")

# 送信ボタン
if st.button("送信する", type="primary"):
    if not message_title:
        st.warning("題名を入力してください。")
    elif not message_text:
        st.warning("詳細テキストを入力してください。")
    elif len(df_filtered) == 0:
        st.error("送信対象がいません。")
    else:
        # 送信対象のIDリストを作成
        user_id_list = df_filtered['id'].tolist()
        
        # 送信処理
        try:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # 画像をアップロードしてURLを取得（LINE Content APIを使用）
            image_url = None
            if uploaded_image:
                try:
                    # 画像を一時的にアップロード（LINE Content APIを使用）
                    # 注意: 実際の実装では、画像をLINE Content APIにアップロードする必要があります
                    # ここでは簡易的にbase64エンコードして送信する方法を検討
                    status_text.text("画像をアップロード中...")
                    # LINE Content APIへのアップロード処理を実装
                    # 今回は、画像なしで送信する方法を実装
                    st.info("画像アップロード機能は実装中です。現在はテキストとリンクのみ送信されます。")
                except Exception as e:
                    st.warning(f"画像のアップロードに失敗しました: {e}")
            
            # メッセージの構築
            messages = []
            
            # リンクがある場合は、ボタンテンプレートメッセージを作成
            if link_url:
                buttons_template = ButtonsTemplate(
                    title=message_title[:40],  # タイトルは最大40文字
                    text=message_text[:120],   # テキストは最大120文字
                    actions=[
                        URITemplateAction(
                            label='詳細を見る',
                            uri=link_url
                        )
                    ]
                )
                template_message = TemplateSendMessage(
                    alt_text=f"{message_title}\n{message_text[:100]}...",
                    template=buttons_template
                )
                messages.append(template_message)
            else:
                # リンクがない場合は、タイトルとテキストを組み合わせたテキストメッセージ
                full_message = f"{message_title}\n\n{message_text}"
                messages.append(TextSendMessage(text=full_message))
            
            # 画像がある場合は、画像メッセージを追加
            # 注意: 実際の実装では、画像をLINE Content APIにアップロードする必要があります
            # if image_url:
            #     messages.append(ImageSendMessage(original_content_url=image_url, preview_image_url=image_url))
            
            # 送信処理（500人ずつ分割）
            total_users = len(user_id_list)
            sent_count = 0
            
            for i in range(0, total_users, 500):
                batch = user_id_list[i:i+500]
                line_bot_api.multicast(batch, messages)
                sent_count += len(batch)
                progress_bar.progress(sent_count / total_users)
                status_text.text(f"送信中... {sent_count}/{total_users}名")
            
            progress_bar.progress(100)
            st.success(f"送信完了！ {total_users} 名に配信しました。")
            status_text.empty()
            
        except LineBotApiError as e:
            st.error(f"送信エラーが発生しました: {e}")
            st.error(f"エラー詳細: {e.error}")
        except Exception as e:
            st.error(f"予期せぬエラーが発生しました: {e}")