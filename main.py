import streamlit as st
import pandas as pd
from linebot import LineBotApi
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError

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

message_text = st.text_area("送るメッセージを入力してください", height=150)

if st.button("送信する", type="primary"):
    if not message_text:
        st.warning("メッセージを入力してください。")
    elif len(df_filtered) == 0:
        st.error("送信対象がいません。")
    else:
        # 送信対象のIDリストを作成
        user_id_list = df_filtered['id'].tolist()
        
        # 送信処理
        try:
            # プログレスバー（進行状況）の表示
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # LINEの仕様上、最大500人まで一度に送れるが、念のためMulticastを使う
            # ※本来は500人ずつ分割する処理が必要だが、今回は人数が少ないのでそのまま送信
            line_bot_api.multicast(user_id_list, TextSendMessage(text=message_text))
            
            progress_bar.progress(100)
            st.success(f"送信完了！ {len(user_id_list)} 名に配信しました。")
            
        except LineBotApiError as e:
            st.error(f"送信エラーが発生しました: {e}")