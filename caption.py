from transformers import pipeline
import requests
import urllib.request
from PIL import Image, ImageFilter
from PIL import ImageDraw
from PIL import ImageFont
import textwrap
import streamlit as st
import nltk
nltk.download("stopwords")
nltk.download("universal_tagset")
import pke

# For a given text as input, this class extracts keywords.
# Unsupervised models available:
# PositionRank (Default)
# TopicRank
# SingleRank
# TextRank
# TopicalPageRank
# MultipartiteRank

class keyword:
    def __init__(self, description, graph_model="PositionRank", n=5):

        if graph_model == "TopicRank":
            extractor = pke.unsupervised.TopicRank()
        elif graph_model == "SingleRank":
            extractor = pke.unsupervised.SingleRank()
        elif graph_model == "TextRank":
            extractor = pke.unsupervised.TextRank()
        elif graph_model == "TopicalPageRank":
            extractor = pke.unsupervised.TopicalPageRank()
        elif graph_model == "PositionRank":
            extractor = pke.unsupervised.PositionRank()
        elif graph_model == "MultipartiteRank":
            extractor = pke.unsupervised.MultipartiteRank()

        extractor = pke.unsupervised.PositionRank()
        extractor.load_document(input=description)
        extractor.candidate_selection()
        extractor.candidate_weighting()
        self.topics = extractor.get_n_best(n)

    # Return a list of topics
    def get_topics(self):
        topic_list = []
        for i in self.topics:
            topic_list.append(i[0])
        return topic_list

class summarizer:
    def summarize(self, description):
        summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        summary = summarizer(description, max_length=150, min_length=30, do_sample=False)
        return summary

def get_image(topics):
    topic = topics[0]
    images = requests.get("https://api.unsplash.com/search/photos?query="+topic+"&orientation=portrait&color=black&page=1&client_id=FBsx0gRhO0n8hRxl1yB-q1MOa0i3rgdQp1b4nUVcnCo")
    data = images.json()
    url_list = []
    for image_url in data.get("results"):
        urls = image_url.get("urls")
        url_list.append(urls.get("regular"))
    return url_list

def download_images(urls):
    image_id = 0
    image_name = []
    for url in urls:
        destination = "Downloads/images/img_" + str(image_id) + ".jpg"
        urllib.request.urlretrieve(url, destination)
        name = "img_" + str(image_id) + ".jpg"
        image_name.append(name)
        image_id += 1
    return image_name

def create_post(description, image_name):
    image_id = 0
    for image in image_name:
        # Open an Image
        source = "Downloads/images/" + image
        destination = "Downloads/output/" + str(image_id) + ".png"
        img = Image.open(source)
        img = img.filter(ImageFilter.GaussianBlur(3))
        w,h = img.size
 
        # Call draw Method to add 2D graphics in an image
        I1 = ImageDraw.Draw(img)
 
        # Custom font style and font size
        myFont = ImageFont.truetype('Rubik-Italic.ttf', 70)
 
        # Add Text to an image
        lines = textwrap.wrap(description, width=30)
        w_, line_height = myFont.getsize(lines[0])
        y_text = ((17 - len(lines))/2 ) * int(line_height)
        for line in lines:
            width, height = myFont.getsize(line)
            I1.text(((w-width)/2, y_text), line, font=myFont, fill =(255, 255, 255))
            y_text += height * 1.5

        # Save the edited image
        img.save(destination)
        image_id += 1

def generate(description):
    state = st.text("Extracting keywords...")

    topic_ob = keyword(description)
    topics = topic_ob.get_topics()

    state.text("Extracting caption...")

    summary_ob = summarizer()
    summary = summary_ob.summarize(description)
    summary = summary[0].get("summary_text")

    state.text("Generating post...")

    image_urls = get_image(topics)
    image_name = download_images(image_urls)
    create_post(summary, image_name)

    state.text("")

    c1,c2,c3 = st.columns(3)
    with c1:
        image = Image.open("Downloads/output/"+str(0)+".png")
        st.image(image, width = 500)
    with c2:
        image = Image.open("Downloads/output/"+str(1)+".png")
        st.image(image, width = 500)
    with c3:
        image = Image.open("Downloads/output/"+str(2)+".png")
        st.image(image, width = 500)

if __name__ == "__main__":
    st.set_page_config(layout="wide")
    default = "Here at 80/20, we believe in food as fuel and that absolutely everybody benefits from clean, natural and unprocessed whole foods. We endeavor to serve you real, healthy, honest and delicious meals as well as nutrient packed smoothies, homemade raw desserts and damn good coffee. We wholeheartedly believe that life is all about balance, and while food is functional it should also be fun!"
    st.title('Social Media Post Generator')
    user_input = st.text_area("Enter Description here...", default, height=200)
    submit = st.button(label="Submit")
    if submit:
        user_input = ''.join(x for x in user_input if x in string.printable)
        generate(user_input)