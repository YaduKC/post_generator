import streamlit as st
from PIL import Image
import io
import openai
import requests
from io import BytesIO
from PIL import Image, ImageFilter
from PIL import ImageDraw
from PIL import ImageFont
import textwrap
import random

unsplash_key = st.secrets["UNSPLASH_KEY"]
openai.api_key = st.secrets["OPENAI_KEY"]
if 'header_' not in st.session_state:
    st.session_state.header_ = ""
if 'tagline_' not in st.session_state:
    st.session_state.tagline_ = ""
if 'hashtags_' not in st.session_state:
    st.session_state.hashtags_ = ""
if 'submit_' not in st.session_state:
    st.session_state.submit_ = False
if 'post_count' not in st.session_state:
    st.session_state.post_count = 0
if 'post_list_' not in st.session_state:
    st.session_state.post_list_ = []
if 'header_dict_' not in st.session_state:
    st.session_state.header_dict_ = {}
    st.session_state.header_dict_["element1"] = ""
    st.session_state.header_dict_["element2"] = ""
    st.session_state.header_dict_["element3"] = ""
    st.session_state.header_dict_["element4"] = ""
    st.session_state.header_dict_["element5"] = ""
if 'image_list_' not in st.session_state:
    st.session_state.image_list_ = []
email_cb = False
website_cb = False
address_cb = False
fb_cb = False
ig_cb = False
tw_cb = False
li_cb = False
yt_cb = False
sc_cb = False

def process_data(data):
    for key, val in data.items():
        if val == "" or val == []:
            val = "None"
        #print(key,val)

    output = {}
    output["hashtags"] = hashtags(data.get("description"))
    output["tagline"] = tagline(data.get("description"), data.get("name"))
    output["header"] = header(data.get("description"), data.get("demography"), data.get("intent"), data.get("tone"), data.get("name"))
    hash_tags = output["hashtags"].split()
    hash_tags = [i[1:] for i in hash_tags]
    output["keywords"] = keywords(output.get("tagline"), data.get("domain"))
    url_list = get_image(hash_tags)
    st.session_state.image_list_ = download_images(url_list)
    st.session_state.post_list_ = create_post(output["tagline"], st.session_state.image_list_)
    return output, st.session_state.post_list_

def get_image(topics):
    url_list = []
    print(topics)
    for topic in topics:
        images = requests.get("https://api.unsplash.com/search/photos?query="+topic+"&orientation=landscape&page=1&client_id=" + unsplash_key)
        #print(images)
        data = images.json()
        result = data.get("results")
        if len(result) > 0:
            urls = result[0].get("urls")
            url_list.append(urls.get("regular"))
            print(urls.get("regular"))
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
    post_list = []
    for index,image in enumerate(images):
        
        r = random.randint(0,255)
        g = random.randint(0,255)
        b = random.randint(0,255)

        lum = (0.299*r + 0.587*g + 0.114*b)
        if lum < 127.5:
            t_col = (255,255,255)
        else:
            t_col = (0,0,0)
        comp = complement(r, g, b)

        img = image
        #img = img.filter(ImageFilter.GaussianBlur(3))
        w,h = img.size
 
        # Call draw Method to add 2D graphics in an image
        I1 = ImageDraw.Draw(img)
 
        # Custom font style and font size
        #req = requests.get("https://github.com/google/fonts/blob/main/apache/opensans/OpenSans-Italic%5Bwdth%2Cwght%5D.ttf?raw=true")
        req = requests.get("https://github.com/google/fonts/blob/main/apache/robotoslab/RobotoSlab%5Bwght%5D.ttf?raw=true")

        myFont = ImageFont.truetype(BytesIO(req.content), 75)
 
        # Add Text to an image
        lines = textwrap.wrap(description, width=30)
        w_, line_height = myFont.getsize(lines[0])
        y_text = h-(len(lines)+1)*int(line_height)
        print(len(lines))
        I1.rectangle(((0,y_text),(w,h)), fill=comp, width=1)
        for line in lines:
            width, height = myFont.getsize(line)
            I1.text(((w-width)/2, y_text), line, font=myFont, fill = t_col)
            y_text += height*1.3
        post_list.append(img)
    return post_list

# Sum of the min & max of (a, b, c)
def hilo(a, b, c):
    if c < b: b, c = c, b
    if b < a: a, b = b, a
    if c < b: b, c = c, b
    return a + c

def complement(r, g, b):
    k = hilo(r, g, b)
    return tuple(k - u for u in (r, g, b))

def keywords(description, domain):
    response = openai.Completion.create(
      engine="davinci",
      prompt="Text: " + description + ". For the business " + domain + "\n\nKeywords:",
      temperature=0.3,
      max_tokens=80,
      top_p=1.0,
      frequency_penalty=0.8,
      presence_penalty=0.0,
      stop=["\n"]
    )
    key = response.choices[0].get("text")
    return list(set(key.split()))

def hashtags(description):

    response = openai.Completion.create(
      engine="davinci-instruct-beta-v3",
      prompt="Write 10 hashtags for social media using the description given below.\n\""+description+"\"",
      temperature=0.7,
      max_tokens=64,
      top_p=1,
      frequency_penalty=0,
      presence_penalty=0
    )
    return response.choices[0].get("text").strip("\n")

def tagline(description, name):

    response = openai.Completion.create(
      engine="davinci-instruct-beta-v3",
      prompt="Write a tagline for the business named \"" + name + "\" using the description given below.\n\""+description+"\"",
      temperature=0.7,
      max_tokens=64,
      top_p=1,
      frequency_penalty=0,
      presence_penalty=0
    )
    return "\"" + response.choices[0].get("text").strip("\n") + "\""

def header(description, demography, intent, tone, name):

    if intent[0] == "Convince": intent = "convincing"
    elif intent[0] == "Inform": intent = "informative"
    elif intent[0] == "Describe": intent = "descriptive"

    response = openai.Completion.create(
      engine="davinci-instruct-beta-v3",
      prompt="Write a 60 word"+ intent +" advertisement for "+ demography[0] +" with an "+ tone[0] +" tone using the description given below for the business named \"" + name + "\".\n\""+description+"\"",
      temperature=0.7,
      max_tokens=100,
      top_p=1,
      frequency_penalty=0,
      presence_penalty=0
    )
    return "\"" + response.choices[0].get("text").strip("\n") + "\""

if __name__ == "__main__":
    input_data = {}
    st.set_page_config(layout="wide")
    st.title("Social Media Post Generator")
    with st.container():
        
        c1, c2 = st.columns(2)
        c1.subheader("Set Goals")
        c2.subheader("Describe Your Post")
        
        demography = c1.selectbox(label="Demography", options=("Children", "Youth", "Adults", "General Audience"))
        intent = c1.selectbox(label="Intent", options=("Inform", "Describe", "Convince"))
        tone = c1.selectbox(label="Tone", options=("Neutral", "Confident", "Joyful", "Optimistic", "Friendly", "Urgent"))
        description = c2.text_area(label="Enter Description", height = 330)

    st.header("Enter Business Details To Be Included In The Post")
    with st.container():
        c1, c2 = st.columns(2)
        c1.subheader("General Details")
        domain = c1.selectbox(label="Domain", options=("Travel", "Food", "Fashion"))
        name = c1.text_input(label="Business Name")
        email = c1.text_input(label="Email")
        website = c1.text_input(label="Domain Website")
        address1 = c1.text_input(label="Address Line 1")
        address2 = c1.text_input(label="Address Line 2")
        city = c1.text_input(label="City")
        state = c1.text_input(label="State")
        post = c1.text_input(label="Post Code")
        country = c1.text_input(label="Country")
        #logo = c1.file_uploader(label="Upload Logo")
        c2.subheader("Social Media Links")
        fb = c2.text_input(label="Facebook")
        ig = c2.text_input(label="Instagram")
        tw = c2.text_input(label="Twitter")
        li = c2.text_input(label="Linkedin")
        yt = c2.text_input(label="YouTube")
        sc = c2.text_input(label="Snapchat")
        submit_button = c1.button(label="Submit", key = 1)

    if submit_button or st.session_state.submit_:
        st.session_state.submit_ = True
        input_data["demography"] = demography
        input_data["intent"] = intent
        input_data["tone"] = tone
        input_data["description"] = description
        input_data["domain"] = domain
        input_data["name"] = name
        input_data["email"] = email
        input_data["website"] = website
        input_data["address1"] = address1
        input_data["address2"] = address2
        input_data["city"] = city
        input_data["state"] = state
        input_data["post"] = post
        input_data["country"] = country
        input_data["fb"] = fb
        input_data["ig"] = ig
        input_data["tw"] = tw
        input_data["li"] = li
        input_data["yt"] = yt
        input_data["sc"] = sc

        address = ""
        if input_data["address1"] != "":
            if input_data["address2"] != "":
                address += input_data["address1"] + ', '
            else:
                address += input_data["address1"] + ',\n'
        if input_data["address2"] != "":
            address += input_data["address2"] + ',\n'
        if input_data["city"] != "":
            address += input_data["city"] + ', '
        if input_data["state"] != "":
            address += input_data["state"] + ', '
        if input_data["country"] != "":
            address += input_data["country"] + ', '
        address += input_data["post"]

        #if logo != None:
        #    bytes_data = logo.getvalue()
        #    imageStream = io.BytesIO(bytes_data)
        #    img = Image.open(imageStream)
        #    input_data["logo"] = logo

        if st.session_state.header_ == "":
            with st.spinner('Processing...'):
                output, post_list = process_data(input_data)
            st.session_state.post_list_ = post_list
            st.session_state.header_ = output.get("header")
            st.session_state.tagline_ = output.get("tagline")
            st.session_state.hashtags_ = output.get("hashtags")

        st.title("Refine")
        st.info("Select elements and press submit")
        st.subheader("Select Image")

        with st.container():
            c1,c2,c3 = st.columns([1,2,1])
            #c2.image(img, width=400)
            print(st.session_state.post_count)
            c2.image(st.session_state.post_list_[st.session_state.post_count], width=600)
            next = c1.button(label="Next")
            prev = c1.button(label="Prev")
            if next:
                st.session_state.post_count += 1
                st.session_state.post_count = st.session_state.post_count%len(st.session_state.post_list_)
                st.experimental_rerun()
            if prev:
                st.session_state.post_count -= 1
                st.session_state.post_count = st.session_state.post_count%len(st.session_state.post_list_)
                st.experimental_rerun()

        with st.container():

            st.session_state.header_dict_["element1"] = st.session_state.header_
            follow = ""
            if input_data.get("website") != "": 
                st.session_state.header_dict_["element2"] =input_data["website"]
            if input_data.get("email") != "":
                st.session_state.header_dict_["element3"] ="Contact us at:\n" + input_data["email"]
            if input_data.get("fb") != "" or input_data.get("ig") != "" or input_data.get("tw") != "" or input_data.get("li") != "" or input_data.get("yt") != "" or input_data.get("sc") != "":
                follow +="Follow us at: "
            if input_data.get("fb") != "":
                follow +="\n" + input_data["fb"]
            if input_data.get("ig") != "":
                follow +="\n" + input_data["ig"]
            if input_data.get("tw") != "":
                follow +="\n" + input_data["tw"]
            if input_data.get("li") != "":
                follow +="\n" + input_data["li"]
            if input_data.get("yt") != "":
                follow +="\n" + input_data["yt"]
            if input_data.get("sc") != "":
                follow +="\n" + input_data["sc"]
            if address != "":
                st.session_state.header_dict_["element4"] ="Visit us at:\n" + address
            st.session_state.header_dict_["element5"] = follow

            with st.container():
                st.header("Header Elements")
                

                st.subheader("Element 1")
                st.text_area(label="", value = st.session_state.header_dict_["element1"])
                with st.container():
                    c1,c2,c3 = st.columns([1,1,4])
                    e1 = c1.checkbox(label="Select")
                    gen_header = c2.button(label="Generate")
                    c3.text("")
                    if gen_header:
                        with c3.container():
                            with st.spinner('Processing...'):
                                st.session_state.header_ = header(input_data.get("description"), input_data.get("demography"), input_data.get("intent"), input_data.get("tone"), input_data.get("name"))
                                st.experimental_rerun()


                st.subheader("Element 2")
                st.info(st.session_state.header_dict_["element2"])
                e2 = st.checkbox(label="Select", key=1)

                st.subheader("Element 3")
                st.info(st.session_state.header_dict_["element3"])
                e3 = st.checkbox(label="Select", key=2)

                st.subheader("Element 4")
                st.info(st.session_state.header_dict_["element4"])
                e4 = st.checkbox(label="Select", key=3)

                st.subheader("Element 5")
                st.info(st.session_state.header_dict_["element5"])
                e5 = st.checkbox(label="Select", key=4)
             
            with st.container():
                st.subheader("Tagline")
                st.text_area(label="", value = st.session_state.tagline_)
                with st.container():
                    c1,c2,c3 = st.columns([1,1,4])
                    tg = c1.checkbox(label="Select", key=5)
                    gen_tag = c2.button(label="Generate", key=1)
                    c3.text("")
                    if gen_tag:
                        with c3.container():
                            with st.spinner('Processing...'):
                                st.session_state.tagline_ = tagline(input_data.get("description"), input_data.get("name"))
                                st.session_state.post_list_ = create_post(st.session_state.tagline_, st.session_state.image_list_)
                                st.experimental_rerun()
            st.subheader("Tags")
            st.info(st.session_state.hashtags_)
            submit_user = st.button(label="Submit") 

            if submit_user:
                final_header = ""
                if e1: 
                    final_header += st.session_state.header_dict_["element1"] + "\n\n"
                if e2: 
                    final_header += st.session_state.header_dict_["element2"] + "\n\n"
                if e3: 
                    final_header += st.session_state.header_dict_["element3"] + "\n\n"
                if e4: 
                    final_header += st.session_state.header_dict_["element4"] + "\n\n"
                if e5: 
                    final_header += st.session_state.header_dict_["element5"]

                with st.container():
                    st.title("Output")
                    c1, c2= st.columns([1,2])
                    c1.header("Image")
                    c2.header("Text Elements")
                    for i in range(12): c1.text("")
                    c2.subheader("Header")
                    c1.image(st.session_state.post_list_[st.session_state.post_count], width=600)
                    c2.text_area(label="", value = final_header, key=6, height=300)
                    if tg:
                        c2.subheader("Tag Line")
                        c2.text_area(label="", value = st.session_state.tagline_, key=7)
                    c2.subheader("Relevant Tags")
                    c2.text_area(label="", value = st.session_state.hashtags_)






                


