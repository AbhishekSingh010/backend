from s3bucket import supabase_client
from fastapi import APIRouter, Depends,File, UploadFile
from utils.auth_utils import get_current_user
import os
import tensorflow as tf
import numpy as np
from PIL import Image
import io
from dotenv import load_dotenv

load_dotenv()

storage_bucket_name=os.getenv("storage_bucket_name")
MODEL_PATH = r"./model/1.h5"  
model = tf.keras.models.load_model(MODEL_PATH,compile=False)


def predict_disease(image_bytes: bytes):
  
   
    class_names = ["Early Blight", "Late Blight", "Healthy"]
    try:
        # convert bytes → image
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        image = image.resize((256, 256))   
        image_array = np.array(image)
        # image_array = image_array / 255.0
        img_batch = np.expand_dims(image_array, axis=0)
        prediction = model.predict(img_batch)

        predicted_class = class_names[np.argmax(prediction[0])]
        confidence =100* float(np.max(prediction[0]))

        return {
            "disease": predicted_class,
            "confidence": confidence
        }

    except Exception as e:
        raise Exception(f"Prediction failed: {str(e)}")










  
def upload_image(image_bytes: bytes, filename,user_id,content_type):
   file_name=f"{user_id}_{filename}"
   try:
        supabase_client.storage.from_(storage_bucket_name).upload(
            file_name,
            image_bytes,
            file_options={"content-type": content_type}
        )
        
   except Exception as e:
        raise Exception(f"Upload failed: {str(e)}")

   image_url = supabase_client.storage.from_(storage_bucket_name).get_public_url(file_name)

   return image_url
 