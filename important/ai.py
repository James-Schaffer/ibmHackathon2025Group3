
import google.generativeai as genai
import os
from PIL import Image

# Set your API key (Make sure to keep this secret and avoid hardcoding in production)
os.environ["GOOGLE_API_KEY"] = "AIzaSyAMnCFsSFcXpOAfQzv05gLk4NuGjymRaLM"

# Configure the Gemini model
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

image_path = r"C:\Users\si258\OneDrive\Desktop\Hackathon Files\uploads\captured_1739104509.png"


if not os.path.exists(image_path):
    print("Error: Image file not found!")
else:
    print("Image file exists. Proceeding...")

image = Image.open(image_path)

# Select the multimodal model (Gemini Pro Vision)
model = genai.GenerativeModel("gemini-1.5-flash")  # ✅ Use the new model


# Send the request with text + image input
response = model.generate_content(["From this image, analyse the names of the products listed and the price of each product.", image])

# Print the response
print(response.text)
