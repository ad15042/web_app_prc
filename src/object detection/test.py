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

## Find the object detection domain
obj_detection_domain = next(domain for domain in trainer.get_domains() 
                            if domain.type == "ObjectDetection" and 
                            domain.name == "General")

## Create a new project
print ("Creating project...")
## Use uuid to avoid project name collisions.
## UUID: Universally Unique IDentifier」の略称。 インターネット上のオブジェクトを識別するための128ビットの文字列
project = trainer.create_project(str(uuid.uuid4()), 
                                 domain_id=obj_detection_domain.id)

# オブジェクトにタグを追加する
## Make two tags in the new project
fork_tag = trainer.create_tag(project.id, "fork")
scissors_tag = trainer.create_tag(project.id, "scissors")


# サンプル画像を対応する領域との座標と共にアップロードする
base_image_location = os.path.join (os.path.dirname(__file__), "images")

## Go through the data table above and create the images
print ("Adding images...")
tagged_images_with_regions = []

# フォーク画像を読み込む
fork_image_regions = image_getter_fork()

for file_name in fork_image_regions.keys():
    x,y,w,h = fork_image_regions[file_name]
    regions = [ Region(tag_id=fork_tag.id, left=x,top=y,width=w,height=h) ]

    with open(os.path.join (base_image_location, 
                            "fork", 
                            file_name + ".jpg"), 
                            mode="rb") as image_contents:
        tagged_images_with_regions.append(ImageFileCreateEntry
                                          (name=file_name, 
                                            contents=image_contents.read(), 
                                            regions=regions))

# ハサミ画像を読み込む
scissors_image_regions = image_getter_scissors()

for file_name in scissors_image_regions.keys():
    x,y,w,h = scissors_image_regions[file_name]
    regions = [ Region(tag_id=scissors_tag.id, left=x,top=y,width=w,height=h) ]

    with open(os.path.join (base_image_location, 
                            "scissors", 
                            file_name + ".jpg"), 
                            mode="rb") as image_contents:
        tagged_images_with_regions.append(ImageFileCreateEntry
                                          (name=file_name, 
                                           contents=image_contents.read(), 
                                           regions=regions))

upload_result = trainer.create_images_from_files(project.id, ImageFileCreateBatch(images=tagged_images_with_regions))
if not upload_result.is_batch_successful:
    print("Image batch upload failed.")
    for image in upload_result.images:
        print("Image status: ", image.status)
    exit(-1)

# プロジェクトをトレーニングする
print ("Training...")
iteration = trainer.train_project(project.id)
print(f'プロジェクトID{project.id}：イテレーション{iteration}')
while (iteration.status != "Completed"):
    iteration = trainer.get_iteration(project.id, iteration.id)
    print ("Training status: " + iteration.status)
    time.sleep(1)

# 現在のイテレーションを公開する
## The iteration is now trained. Publish it to the project endpoint
trainer.publish_iteration(project.id, 
                          iteration.id, 
                          publish_iteration_name, 
                          prediction_resource_id)
print ("Done!")

# 予測エンドポイントをテストする
# Now there is a trained endpoint that can be used to make a prediction

# Open the sample image and get back the prediction results.
with open(os.path.join (base_image_location, "test", "test_image.jpg"),
           mode="rb") as test_data:
    results = predictor.detect_image(project.id, 
                                     publish_iteration_name, 
                                     test_data)

# Display the results.    
for prediction in results.predictions:
    print("\t" + prediction.tag_name + 
          ": {0:.2f}% bbox.left = {1:.2f}, bbox.top = {2:.2f}, bbox.width = {3:.2f}, bbox.height = {4:.2f}"
          .format(prediction.probability * 100, 
                  prediction.bounding_box.left, 
                  prediction.bounding_box.top, 
                  prediction.bounding_box.width, 
                  prediction.bounding_box.height))
    

