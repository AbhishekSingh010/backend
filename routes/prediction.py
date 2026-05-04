from fastapi import APIRouter, Depends,File, HTTPException, UploadFile

from db import get_connection
from utils.auth_utils import get_current_user
from utils.prediction_utils import predict_disease, upload_image
import uuid

router = APIRouter()


@router.get("/history")
def get_history(user=Depends(get_current_user)):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        print("USER PAYLOAD:", user)  # 👈 debug

        # user_id = user.get("user_id")
        # user_id = uuid.UUID(user.get("user_id"))
        user_id_string = user.get("user_id")
        cursor.execute(
            """
            SELECT pred_id, image_url, prediction, confidence, created_at
            FROM predictions
            WHERE user_id = %s
            ORDER BY created_at DESC
            """,
            (user_id_string,)
        )

        rows = cursor.fetchall()
        print("RAW DB ROWS:", rows)  # 👈 debug
        history = []
        for row in rows:
            print("ROW:", row)  # 👈 debug

            history.append({
                "id": row[0],
                "image_url": row[1],
                "prediction": row[2],
                "confidence": float(row[3]),
                "created_at": str(row[4])  
            })
        print("HISTORY:", history)
        cursor.close()
        conn.close()
        
        return history

    except Exception as e:
        print("🔥 FULL ERROR:", e)   
        raise HTTPException(status_code=500, detail=str(e))
  


  

@router.post("/")
def predict(file: UploadFile = File(...), user=Depends(get_current_user)):
    # read image
    image_bytes = file.file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Invalid image file")

    # run ML model
    result = predict_disease(image_bytes)
    prediction = result["disease"]
    confidence = result["confidence"]
    confidence_new = round(confidence, 2)   
    
    # upload image to storage S3
    content_type = file.content_type
    image_url = upload_image(image_bytes,file.filename, user["user_id"],content_type)
    
    
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO predictions (user_id, image_url, prediction, confidence)
        VALUES (%s, %s, %s, %s)
        """,
        (user["user_id"], image_url, prediction, confidence_new)
    )

    conn.commit()
    cursor.close()
    conn.close()

    return {
        "prediction": prediction,
        "confidence": f"{confidence_new:.2f}",
        "image_url": image_url,
        "message": "prediction with image saved in database"
    }
