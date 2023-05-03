# ベースイメージ
FROM python:3

# 環境変数を設定
ENV PYTHONIOENCODING utf-8

# app/ディレクトリを作成
WORKDIR /app

# パッケージをインストールする準備
RUN apt update
RUN apt install -y
RUN apt install -y python3-pip
RUN pip install --upgrade pip
RUN pip install azure-cognitiveservices-vision-customvision

# requirements.txtをコンテナ側にコピー
COPY requirements.txt /app

# requirements.txtに記載されたパッケージをインストールする
RUN pip install -r requirements.txt

# ローカル側のstreamlit-appディレクトリ配下にあるファイルをコンテナ側のappディレクトリにコピー
COPY ./src/ /app
