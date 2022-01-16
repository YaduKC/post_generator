import openai
import requests
from google.cloud import storage
from PIL import Image
import io
from imgix import UrlBuilder

class open_ai:

    def __init__(self):
        openai.api_key = "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"
        self.storage_client = storage.Client.from_service_account_json('creds.json')
        self.url = UrlBuilder("captionai.imgix.net", include_library_param=False)

    def imgix_url(self, image="~text", param={}):
        return self.url.create_url(image, param)


    def upload_image(self, destination_blob_name, file):
        bucket = self.storage_client.bucket("captionai")
        blob = bucket.blob(destination_blob_name)

        blob.upload_from_string(file)
        print("done!")

    def product_description(self, description, name, num_responses=1):
        desc = []
        for i in range(num_responses):
            response = openai.Completion.create(
                engine="davinci-instruct-beta-v3",
                prompt="Write a fake marketting for a product called \""+name+"\" \n\""+description+"\".",
                temperature=1.0,
                max_tokens=200,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            desc.append(response.choices[0].get("text").strip("\n"))
        return desc

    def tagline(self, description, name, num_responses=1):
        taglines = []
        for i in range(num_responses):
            response = openai.Completion.create(
              engine="davinci-instruct-beta-v3",
              prompt="Write a tagline for the business named \"" + name + "\" using the description given below.\n\""+description+"\"",
              temperature=1,
              max_tokens=64,
              top_p=1,
              frequency_penalty=0,
              presence_penalty=0
            )
            taglines.append( "\"" + response.choices[0].get("text").strip("\n") + "\"")
        return taglines

    def hashtag(self, description, num_responses=1):
        hashtags = []
        for i in range(num_responses):
            response = openai.Completion.create(
              engine="davinci-instruct-beta-v3",
              prompt="Write 10 hashtags for social media using the description given below.\n\""+description+"\"",
              temperature=0.7,
              max_tokens=64,
              top_p=1,
              frequency_penalty=0,
              presence_penalty=0
            )
            hashtags.append(response.choices[0].get("text").strip("\n"))
        return hashtags

    def header(self, description, demography, intent, tone, name):

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

#ob = open_ai()
#im = Image.open("img.jpg")
#buf = io.BytesIO()
#im.save(buf, format='JPEG')
#byte_im = buf.getvalue()
#ob.upload_image("test.jpg", byte_im)




