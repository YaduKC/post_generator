import os
import openai
import requests
import urllib.request
from PIL import Image, ImageFilter
from PIL import ImageDraw
from PIL import ImageFont
import textwrap
import streamlit as st
import string
from io import BytesIO

def keywords(text):
    openai.api_key = st.secrets["OPENAI_KEY"]
    p = "Text: " + text + "\n\nKeywords:"
    response = openai.Completion.create(
      engine="davinci",
      prompt=p,
      temperature=0.3,
      max_tokens=80,
      top_p=1.0,
      frequency_penalty=0.8,
      presence_penalty=0.0,
      stop=["\n"]
    )
    key = response.choices[0].get("text")
    return list(set(key.split()))

def get_captions(text):
    openai.api_key = st.secrets["OPENAI_KEY"]
    p = "Write a creative ad for the following product to run on Social media:\n\"\"\"\"\"\"\n" + text + "\n\"\"\"\"\"\"\nThis is the ad I wrote for Social media aimed at general audience:\n\"\"\"\"\"\""
    response = openai.Completion.create(
      engine="davinci-instruct-beta",
      prompt=p,
      temperature=0.5,
      max_tokens=50,
      top_p=1.0,
      frequency_penalty=0.0,
      presence_penalty=0.0,
      stop=["\"\"\"\"\"\""]
    )
    return response.choices[0].get("text")

def get_image(topics):
    url_list = []
    for topic in topics:
        key = st.secrets["UNSPLASH_KEY"]
        images = requests.get("https://api.unsplash.com/search/photos?query="+topic+"&orientation=portrait&color=black&page=1&client_id=" + key)
        data = images.json()
        result = data.get("results")
        if len(result) > 0:
            urls = result[0].get("urls")
            url_list.append(urls.get("regular"))
        else:
            url_list.append(-1)
    return url_list

def download_images(urls):
    image = []
    for url in urls:
        if url != -1:
            response = requests.get(url)
            img = Image.open(BytesIO(response.content))
            image.append(img)
    return image

def create_post(description, images):

    for index,image in enumerate(images):
        
        img = image
        img = img.filter(ImageFilter.GaussianBlur(3))
        w,h = img.size
 
        # Call draw Method to add 2D graphics in an image
        I1 = ImageDraw.Draw(img)
 
        # Custom font style and font size
        req = requests.get("https://github.com/google/fonts/blob/main/apache/montez/Montez-Regular.ttf?raw=true")

        myFont = ImageFont.truetype(BytesIO(req.content), 70)
 
        # Add Text to an image
        lines = textwrap.wrap(description[index], width=30)
        w_, line_height = myFont.getsize(lines[0])
        y_text = ((17 - len(lines))/2 ) * int(line_height)
        for line in lines:
            width, height = myFont.getsize(line)
            I1.text(((w-width)/2, y_text), line, font=myFont, fill =(255, 255, 255))
            y_text += height * 1.5
        st.image(img, width = 500)
    

if __name__ == "__main__":
    st.title('Social Media Post Generator')
    default = "Here at 80/20, we believe in food as fuel and that absolutely everybody benefits from clean, natural and unprocessed whole foods. We endeavor to serve you real, healthy, honest and delicious meals as well as nutrient packed smoothies, homemade raw desserts and damn good coffee. We wholeheartedly believe that life is all about balance, and while food is functional it should also be fun!"
    user_input = st.text_area("Enter Description here...", default, height=200)
    c1, c2 = st.columns(2)
    submit = c1.button(label="Submit")
    info = c2.text("")
    if submit:
        user_input = ''.join(x for x in user_input if x in string.printable)
        info.text("Extracting Keywords...")
        key_list = keywords(user_input)
        info.text("Downloading images...")
        image_url = get_image(key_list)
        image = download_images(image_url)
        info.text("Generating captions...")
        captions = []
        for key in key_list:
            new_cap = get_captions(user_input)
            new_cap = new_cap.split(".")[:-1]
            new_cap = ". ".join(new_cap)
            captions.append(new_cap)
        info.text("Creating posts...")
        create_post(captions, image)
        info.text("Done...")
        
   


    



    