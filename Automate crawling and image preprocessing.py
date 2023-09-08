# Specify the search terms for web scraping and image download
query_list = [['cat'], ['dog']]
# Number of images to download
down_img_count = 3
# Image refinement settings: enable (True) or disable (False)
resize = True
resize_size = 244 # Size (244,244)
# Histogram equalization
equalizeHist = True
# Affine transformation
Affine = True
# Gaussian blur
Gauss = True
# Brightness adjustment
Bright = True
offset = 50
# Contrast adjustment
Clahe = True
# Vertical flip
VerticalFlip = True
# Horizontal flip
HorizontalFlip = True


import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

import time
import os
import urllib, requests
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
import cv2
import numpy as np
import albumentations as A
from tqdm import tqdm

transform = A.Compose([
    A.CLAHE(),
    A.RandomRotate90(),
    A.Transpose(),
    A.ShiftScaleRotate(scale_limit=0.50, p=0.75),
    A.Blur(blur_limit=3),
    A.OpticalDistortion(),
    A.GridDistortion(),
    A.HueSaturationValue()
])
transform = A.Compose([
    A.OneOf([
        A.MotionBlur(p=0.2),
        A.MedianBlur(blur_limit=3, p=0.1),
        A.Blur(blur_limit=3, p=0.1)
    ], p=1.0),
])

service = Service(ChromeDriverManager().install())

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')

driver = webdriver.Chrome(service=service, options= chrome_options)


for query in tqdm(query_list, desc = 'Current status'):
    driver.get("https://www.google.co.kr/imghp?h1")
    search_box = driver.find_element(By.CLASS_NAME, "gLFyf")
    search_box.clear()
    search_box.send_keys(query)
    search_box.submit()

    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")    
        time.sleep(0.1)

        new_height = driver.execute_script("return document.body.scrollHeight")

        if new_height == last_height:
            elem = driver.find_element(By.CLASS_NAME, "FAGjZe")
        
            if "" == str(elem.get_attribute('style')).strip():
                driver.find_element(By.CLASS_NAME, "LZ4I").click()
            
            if "3" == str(driver.find_element(By.CLASS_NAME, "DwpMZe ").get_attribute("data-status")):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                break


        last_height = new_height
        
        images = driver.find_elements(By.CSS_SELECTOR, "img.rg_i.Q4LuWd")
        links = []

        for image in images:
            if image.get_attribute('src') is not None:
                links.append(image.get_attribute('src'))
            elif image.get_attribute('data-src') is not None:
                links.append(image.get_attribute('data-src'))
            elif image.get_attribute('data-iurl') is not None:
                links.append(image.get_attribute('data-iurl'))
    print(f"{query} Number of images retrieved : {len(links)}")
    print(f"Number of images to download : {down_img_count}")
    
    count = 0
    for i in links : 
        start = time.time()
        url = i
        os.makedirs(f"./{query}_img_download/", exist_ok=True)
        if count < down_img_count:
            while True:
                try:
                    urllib.request.urlretrieve(url, f"./{query}_img_download/{str(count)}_{query}.png")
                    print(f"{str(count + 1)} / {down_img_count} / {query} / Download time required : {str(time.time() - start)[:5]} S")
                    break
                except urllib.error.HTTPError as e:
                    print(f"HTTPError ({e}): Retry...")
                    time.sleep(5)
                except Exception as e:
                    print(f"Error ({e}): Retry...")
                    time.sleep(5)
                if time.time() - start > 60:
                    print(f"{query} Image download failed")
                    break
            count = count + 1 


    print(f"{query_list} Image download complete")
    input = f"./{query}_img_download"
    output = f"./cleaned_images_{query}"

    os.makedirs(output, exist_ok=True)

    images = os.listdir(input)
    count = 0

    for image in images:
        input_path = os.path.join(input, image)
        output_path = os.path.join(output, image)

        img = cv2.imread(input_path)

        with Image.open(input_path) as img:
                if resize:
                    img = img.resize((resize_size, resize_size))
                    if equalizeHist:
                        equal = os.path.join(output,'Equal')
                        os.makedirs(equal, exist_ok=True)
                        equal_path = os.path.join(equal, f"{count}.png")

                        img_np = np.array(img)
                        gray_image = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)
                        equal_img = cv2.equalizeHist(gray_image)
                        cv2.imwrite(equal_path, equal_img)

                    if Affine:
                        affine = os.path.join(output,'Affine')
                        os.makedirs(affine, exist_ok=True)
                        affine_path = os.path.join(affine, f"{count}.png")

                        width, height = img.size
                        angle = np.random.randint(-361, 361)
                        center = (width // 2, height // 2)
                        rot_mat = cv2.getRotationMatrix2D(center, angle, scale=1.0)
                        img_np = np.array(img)
                        affine_img = cv2.warpAffine(img_np, rot_mat, (width, height))
                        affine_pil = Image.fromarray(affine_img)
                        affine_pil.save(affine_path)


                    if Gauss:
                        gauss = os.path.join(output,'Gauss')
                        os.makedirs(gauss, exist_ok=True)
                        gauss_path = os.path.join(gauss, f"{count}.png")


                        mean, var = 0, 1
                        sigma = var ** 0.5
                        img_np = np.array(img)
                        gauss = np.random.normal(mean, sigma, img_np.shape).astype("uint8")
                        gauss_img = cv2.add(img_np, gauss)
                        gaussed_img = cv2.cvtColor(gauss_img, cv2.COLOR_BGR2RGB)
                        cv2.imwrite(gauss_path, gaussed_img)


                    if Bright:
                            bright = os.path.join(output,'Bright')
                            os.makedirs(bright, exist_ok=True)
                            bright_path = os.path.join(bright, f"{count}.png")

                            img_np = np.array(img)
                            bright_img = cv2.convertScaleAbs(img_np, alpha=1, beta=offset)
                            brighted_img = cv2.cvtColor(bright_img, cv2.COLOR_BGR2RGB)
                            cv2.imwrite(bright_path, brighted_img)


                    if Clahe:
                            clahe = os.path.join(output, 'Clahe')
                            os.makedirs(clahe, exist_ok=True)
                            clahe_path = os.path.join(clahe, f"{count}.png")

                            img_np = np.array(img)
                            img_rgb = cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB)
                            transform = A.CLAHE(clip_limit=2.0, tile_grid_size=(8, 8), always_apply=True)
                            clahe_img = transform(image=img_rgb)["image"]
                            cv2.imwrite(clahe_path, clahe_img)

                    if VerticalFlip: 
                        vertical_flip = os.path.join(output, 'VerticalFlip')
                        os.makedirs(vertical_flip, exist_ok=True)
                        vertical_flip_path = os.path.join(vertical_flip, f"{count}.png")

                        img_np = np.array(img)
                        vertical_flip_img = cv2.flip(img_np, 0)
                        vertical_flip_img_rgb = cv2.cvtColor(vertical_flip_img, cv2.COLOR_BGR2RGB)
                        cv2.imwrite(vertical_flip_path, vertical_flip_img_rgb)


                    if HorizontalFlip:
                        horizontal_flip = os.path.join(output, 'HorizontalFlip')
                        os.makedirs(horizontal_flip, exist_ok=True)
                        horizontal_flip_path = os.path.join(horizontal_flip, f"{count}.png")

                        img_np = np.array(img)
                        horizontal_flip_img = cv2.flip(img_np, 1)
                        horizontal_flip_img_rgb = cv2.cvtColor(horizontal_flip_img, cv2.COLOR_BGR2RGB)
                        cv2.imwrite(horizontal_flip_path, horizontal_flip_img_rgb)
                        dd

                    else:
                        img.save(output_path)
        count = count +1

    print(f"{query}Dataset preprocessing complete")
    

