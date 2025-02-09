import google.generativeai as genai
import os
from PIL import Image
import warnings

# Suppress specific warnings (or all warnings)
warnings.filterwarnings("ignore")

# Set your API key (Make sure to keep this secret and avoid hardcoding in production)
os.environ["GOOGLE_API_KEY"] = "AIzaSyAMnCFsSFcXpOAfQzv05gLk4NuGjymRaLM"

# Configure the Gemini model
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

image_path = r"media/image.png"

if not os.path.exists(image_path):
    print("Error: Image file not found!")
else:
    print("Image file exists. Proceeding...")

image = Image.open(image_path)

# Select the multimodal model (Gemini Pro Vision)
model = genai.GenerativeModel("gemini-1.5-flash")

# Send the request with text + image input
response = model.generate_content(["From this image, analyse the names of the products listed and the price of each product and output in this format {item},{price}, no other response and comma after each item or price", image])

# Print the response
lis = response.text.replace("\n","").split(",")
print(lis)
