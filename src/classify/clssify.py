from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from azure.cognitiveservices.vision.customvision.training.models import ImageFileCreateBatch, ImageFileCreateEntry, Region
from msrest.authentication import ApiKeyCredentials
import os, time, uuid
import json

class Classify:
    
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
    
    publish_iteration_name = "classifyModel"

    credentials = ApiKeyCredentials(in_headers={"Training-key": training_key})
    trainer = CustomVisionTrainingClient(ENDPOINT_TR, credentials)

    # プロジェクトIDを発行し、新規プロジェクトを作成する
    project_name = 0
    if project_name == 0:
        project = ""

    
    def make_trainning(): 
        Classify.project_name = uuid.uuid4()
        Classify.project = Classify.trainer.create_project(Classify.project_name)

        # プロジェクトにタグを追加する
        aconitum_tag = Classify.trainer.create_tag(Classify.project.id, "aconitum")
        parasenecio_del_tag = Classify.trainer.create_tag(Classify.project.id, "parasenecio delphiniifolius")

        # 画像をアップロードし、タグ付けをする
        base_image_location = os.path.join (os.path.dirname(__file__), "Images")

        print("Adding images...")

        image_list = []

        # トリカブトの画像を準備
        for image_num in range(1, 16):
            file_name = "Aconitum{}.jpeg".format(str(image_num).zfill(2))
            with open(os.path.join (base_image_location, "aconitum", file_name), "rb") as image_contents:
                image_list.append(ImageFileCreateEntry
                                (name=file_name, 
                                contents=image_contents.read(), 
                                tag_ids=[aconitum_tag.id]))
                
        # モミジガサの画像を準備
        for image_num in range(1, 16):
            file_name = "Parasenecio_delphiniifolius{}.jpeg".format(str(image_num).zfill(2))
            with open(os.path.join (base_image_location, "parasenecio delphiniifolius", file_name), "rb") as image_contents:
                image_list.append(ImageFileCreateEntry
                                (name=file_name, 
                                contents=image_contents.read(), 
                                tag_ids=[parasenecio_del_tag.id]))

        # 画像イメージのアップロード 
        upload_result = Classify.trainer.create_images_from_files(Classify.project.id, ImageFileCreateBatch(images=image_list))
        if not upload_result.is_batch_successful:
            print("Image batch upload failed.")
            for image in upload_result.images:
                print("Image status: ", image.status)
            exit(-1)

        # プロジェクトのトレーニング
        print ("Training...")
        iteration = Classify.trainer.train_project(Classify.project.id)
        while (iteration.status != "Completed"):
            iteration = Classify.trainer.get_iteration(Classify.project.id, iteration.id)
            print ("Training status: " + iteration.status)
            print ("Waiting 10 seconds...")
            time.sleep(10)

        # イテレーションの公開
        # イテレーションを学習、その後プロジェクトエンドポイントにパブリッシュする
        Classify.trainer.publish_iteration(Classify.project.id, 
                                iteration.id, 
                                Classify.publish_iteration_name, 
                                Classify.prediction_resource_id)
        print ("Done!")

    # 予測エンドポイントをテストする
    # Now there is a trained endpoint that can be used to make a prediction
    def make_prediction(filepath):
        prediction_credentials = ApiKeyCredentials(in_headers={"Prediction-key": Classify.prediction_key})
        predictor = CustomVisionPredictionClient(Classify.ENDPOINT_PR, prediction_credentials)

        # with open(os.path.join (base_image_location, "Test/test_image.jpeg"), "rb") as image_contents:
        with open(filepath, "rb") as image_contents:    
            results = predictor.classify_image(
                Classify.project.id, Classify.publish_iteration_name, image_contents.read())

            # 結果を表示する
            # for prediction in results.predictions:
            #     print("\t" + prediction.tag_name +
            #         ": {0:.2f}%".format(prediction.probability * 100))

            # 結果を返す
            for prediction in results.predictions:
                return prediction.tag_name, prediction.probability
        
        


