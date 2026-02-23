import requests
import json

url = "http://127.0.0.1:8000/predict"

headers = {
    "Authorization": "Bearer test_token"
}

data = {
    "front_pose_type": "front",
    "back_pose_type": "back",
    "token": "test_token"
}

# we need actual images or the server will throw 400
from PIL import Image
import io

img = Image.new('RGB', (100, 100), color = 'red')
img_byte_arr = io.BytesIO()
img.save(img_byte_arr, format='JPEG')
img_bytes = img_byte_arr.getvalue()

files = {
    "front_image": ("front.jpg", img_bytes, "image/jpeg"),
    "back_image": ("back.jpg", img_bytes, "image/jpeg")
}

try:
    response = requests.post(url, data=data, files=files, headers=headers)
    print(response.status_code)
    print(response.text)
except Exception as e:
    print(f"Error: {e}")
