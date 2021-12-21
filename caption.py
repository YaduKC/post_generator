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

def keywords(text):
    openai.api_key = "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"
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
    openai.api_key = "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"
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
        images = requests.get("https://api.unsplash.com/search/photos?query="+topic+"&orientation=portrait&color=black&page=1&client_id=FBsx0gRhO0n8hRxl1yB-q1MOa0i3rgdQp1b4nUVcnCo")
        data = images.json()
        result = data.get("results")
        if len(result) > 0:
            urls = result[0].get("urls")
            url_list.append(urls.get("regular"))
        else:
            url_list.append(-1)
    return url_list

def download_images(urls, topics):
    image_id = 0
    image_name = []
    for index,url in enumerate(urls):
        if url != -1:
            name = topics[index] + str(image_id) + ".jpg"
            destination = "Downloads/images/img_" + name
            urllib.request.urlretrieve(url, destination)
            image_name.append(name)
            image_id += 1
    return image_name

def create_post(description, image_name):
    image_id = 0
    dest = []
    for index,image in enumerate(image_name):
        # Open an Image
        source = "Downloads/images/"+"img_" + image
        destination = "Downloads/output/" + str(image_id) + ".png"
        dest.append(destination)
        img = Image.open(source)
        img = img.filter(ImageFilter.GaussianBlur(3))
        w,h = img.size
 
        # Call draw Method to add 2D graphics in an image
        I1 = ImageDraw.Draw(img)
 
        # Custom font style and font size
        myFont = ImageFont.truetype('Rubik-Italic.ttf', 70)
 
        # Add Text to an image
        lines = textwrap.wrap(description[index], width=30)
        w_, line_height = myFont.getsize(lines[0])
        y_text = ((17 - len(lines))/2 ) * int(line_height)
        for line in lines:
            width, height = myFont.getsize(line)
            I1.text(((w-width)/2, y_text), line, font=myFont, fill =(255, 255, 255))
            y_text += height * 1.5

        # Save the edited image
        img.save(destination)
        image_id += 1
    return dest

def remove_after_use():
    for file in os.listdir('Downloads/images/'):
        if file.endswith('.jpg'):
            os.remove('Downloads/images/' + file)
    for file in os.listdir('Downloads/output/'):
        if file.endswith('.png'):
            os.remove('Downloads/output/' + file)


def display_image(image_name):
    image = Image.open(image_name)
    st.image(image, width = 500)

if __name__ == "__main__":
    st.title('Social Media Post Generator')
    default = "Here at 80/20, we believe in food as fuel and that absolutely everybody benefits from clean, natural and unprocessed whole foods. We endeavor to serve you real, healthy, honest and delicious meals as well as nutrient packed smoothies, homemade raw desserts and damn good coffee. We wholeheartedly believe that life is all about balance, and while food is functional it should also be fun!"
    user_input = st.text_area("Enter Description here...", default, height=200)
    c1, c2 = st.columns(2)
    submit = c1.button(label="Submit")
    info = c2.text("")
    if submit:
        remove_after_use()
        user_input = ''.join(x for x in user_input if x in string.printable)
        info.text("Extracting Keywords...")
        key_list = keywords(user_input)
        info.text("Downloading images...")
        image_url = get_image(key_list)
        image_names = download_images(image_url, key_list)
        info.text("Generating captions...")
        captions = []
        for key in key_list:
            new_cap = get_captions(user_input)
            unwanted = new_cap.find("This is the ad")
            unwanted = new_cap.find("The ad")
            if unwanted != -1:
                captions.append(new_cap[0:unwanted])
            else:
                captions.append(new_cap)
        info.text("Creating posts...")
        output_list = create_post(captions, image_names)
        for i in output_list:
            display_image(i)
        info.text("Done...")
        
   


    



    