# coding: UTF-8

from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from azure.cognitiveservices.vision.customvision.training.models import ImageFileCreateBatch, ImageFileCreateEntry, Region
from msrest.authentication import ApiKeyCredentials
from image import image_getter_fork, image_getter_scissors
import os, time, uuid
import json

# シークレットキーとエンドポイントの読み込み
with open ("secret.json") as file:
    secret = json.load(file)
    ENDPOINT_TR = secret["ENDPOINT_TR"]
    ENDPOINT_PR = secret["ENDPOINT_PR"]
    training_key = secret['training_key']
    prediction_key = secret["prediction_key"]
    prediction_resource_id = secret["prediction_resource_id"]


# クライアントを認証する
credentials = ApiKeyCredentials(in_headers={"Training-key": training_key})
## CustomVisionTrainingClient：モデルの作成、トレーニング、および公開を処理する
trainer = CustomVisionTrainingClient(ENDPOINT_TR, credentials)
prediction_credentials = ApiKeyCredentials(in_headers={"Prediction-key": prediction_key})
## CustomVisionPredictionClient：物体検出予測のために、モデルに対するクエリ実行を処理する
predictor = CustomVisionPredictionClient(ENDPOINT_PR, prediction_credentials)


# 新しい Custom Vision プロジェクトを作成する
publish_iteration_name = "detectModel"

## オブジェクト検出ドメインを見つける
obj_detection_domain = next(domain for domain in trainer.get_domains() 
                            if domain.type == "ObjectDetection" and 
                            domain.name == "General")

## uuidを使用することでプロジェクト間の衝突を回避する
project = trainer.create_project(str(uuid.uuid4()), 
                                 domain_id=obj_detection_domain.id)

# オブジェクトにタグを追加する
aconitum_tag = trainer.create_tag(project.id, "aconitum")
parasenecio_delphiniifolius_tag = trainer.create_tag(project.id, "parasenecio_delphiniifolius")


# サンプル画像を対応する領域との座標と共にアップロードする
base_image_location = os.path.join (os.path.dirname(__file__), "images")


