import streamlit as st
import numpy as np
import pandas as pd
from PIL import Image
import time

st.title("Streamlit 超入門")

st.write("DataFrame")

df = pd.DataFrame({
    '1列目': [1,2,3,4],
    '2列目':[10,100,1000,10000]
})

# 表の表示方法は２種類ある。
# st.write(df)
# 以下の書き方にすると、縦横比などの引数によって表の表示を変えることができる。
# 列のソートもいじることができる。(昇順、降順)
st.dataframe(df.style.highlight_max(axis=0), width=500, height=600)
# 静的な表を作りたいときは以下
# st.table(df)

# magicツール
# markdown記法を使うことができる。
"""
# 章
## 節
### 項

'''python
import streamlit as st
import numpy as np
import pandas as pd
'''
"""

# 折れ線グラフ
# データ作成
df_ore = pd.DataFrame(
    np.random.rand(20,3),
    columns=['a', 'b', 'c']
)
# 折れ線グラフの作成
st.line_chart(df_ore)
# 他に色々なグラフを指定することができる。

# マップ
# マッピングする位置データの作成
df_map = pd.DataFrame(
    np.random.rand(100,2)/[50, 50] + [35.69, 139.70] # 乱数に新宿付近の緯度経度を足し算,
    columns=['lat', 'lod']
)
# マップの作成
st.line_map(df_map)

## インタラクティブなウィジェット

# チェックボックス
if st.checkbox('Show Image'):
    # 画像表示
    st.write("Display Image")
    img = Image.open('sample.jpeg')
    st.image(img, caption='water jellyfish', use_column_width=True)
    # 画像以外のメディアも表示することができる。

# セレクトボックス
option = st.selectbox(
    'あなたが好きな数字を教えてください。'
    list(range(1, 11))
)

st.write('あなたが好きな数字は', option, 'です。')

# テキストボックス
text = st.text_input('あなたの趣味を教えてください。')
st.write('あなたが好きな趣味は', text, 'です。')

# スライダー (最小値, 最大値, 初期値)
condition = st.slider('あなたの今の調子は？', 0, 100, 50)
st.write('コンディション：', condition)

## レイアウト

# サイドバー (.sidebar.)
condition = st.sidebar.slider('あなたの今の調子は？', 0, 100, 50)

# 2カラム
left_column, right_column = st.beta_columns(2) # 引数にカラム数
# 各カラム毎で表示を分ける場合
button = left_column.button('右からむに文字を表示')
if button:
    right_column.write('ここは右カラム')

# エキスパンダ
expander = st.beta_expander('問合せ')
expander.write('問合せ内容を書く')

## プログレスパー
'Start!!'

latest_iteration = st.empty()
bar = st.progress(0)

for i in range(100):
    latest_iteration.text(f'Iteration{i+1}')
    bar.progress(i+1)
    time.sleep(0.1)

"Done!!"


