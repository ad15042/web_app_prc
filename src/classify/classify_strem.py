import streamlit as st
from PIL import  Image
import os
from clssify import Classify


st.title('トリカブト分類アプリ')

st.markdown("**学習中**")
Classify.make_trainning()


uploaded_image = st.file_uploader("Choose an image...", type=['jpg','jpeg','png'])



# ファイルが存在する場合、画像を表示する。
if uploaded_image:
    img = Image.open(uploaded_image)
    # テスト用画像の格納フォルダ
    base_image_location = os.path.join (os.path.dirname(__file__), "Images/Test/")
    st.image(img)
    
    # フォルダに画像がない場合は保存する
    if not os.path.exists(os.path.join(base_image_location,uploaded_image.name)):
        img.save(os.path.join(base_image_location, uploaded_image))
    else:
        pass
    
    tag_name, prediction = Classify.make_prediction(os.path.join(base_image_location, uploaded_image.name))










    
    st.markdown("*予測結果*")
    st.markdown(tag_name + ":" + prediction*100 + "%")



