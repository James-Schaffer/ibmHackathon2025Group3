import os
from google.generativeai import text

# Set your Gemini API key
os.environ["GOOGLE_API_KEY"] = "AIzaSyAMnCFsSFcXpOAfQzv05gLk4NuGjymRaLM"

# Load the image
image = open("media/captured_image", "rb").read()

# Create a text request
request = text.GenerateTextRequest(
    model="models/gemini-pro",
    prompt=text.TextPrompt(
        text="What is in this image?",
        image=image,
    ),
)

# Send the request to the Gemini API
response = text.generate_text(request)

# Print the response
print(response.result)