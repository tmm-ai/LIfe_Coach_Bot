from picamera import PiCamera
from time import sleep
import cv2
from luxand import luxand
from API_keys import luxand_API


def take_photo():
    """""
    This take a photo of the user right after giving a vocal response. The image is th flipped and sent to the
    luxand API to get an emotion expression reading. A lot other data is provided such as age, gender, etc and 
    this is all filtered out. The emotion data is broken out into keys (emotions) and values (% estimations) and
    then returned as two lists
    
    Input: None
    Output: Two lists, one with emotion labels, and the other emotion level estimations. 
    """""
    # initilizing camera and taking photo
    camera = PiCamera()
    camera.start_preview()
    camera.capture('original.jpg')
    path = r'original.jpg'

    # flipping the photo due to camera orientation upside down
    src = cv2.imread(path)
    image = cv2.flip(src, 0)
    cv2.imwrite('face_photo.jpg', image)

    # connecting to luxand API and getting emotion readings in dictionary
    face_expressions = luxand_API.emotions(photo='face_photo.jpg')
    f_keys = ["Facial Expressions:"]
    f_vals = [" "]
    if not face_expressions:
        print("No face in photo**")
        camera.close()
        return f_keys, f_vals

    # emotion data is the last value in the dictionary, tis value is also a dictionary, here i unpack
    for idx, val in enumerate(face_expressions):
        emotions_dict_all = val
    face_keys = []
    face_values = []
    emotions_dict = emotions_dict_all["emotions"]
    for key, val in emotions_dict.items():
        face_keys.append(key)
        face_values.append(val)
    f_keys += face_keys
    f_vals += face_values
    print("f_keys:", f_keys, f_vals)
    camera.close()

    return f_keys, f_vals

if __name__ == '__main__':
    take_photo()
