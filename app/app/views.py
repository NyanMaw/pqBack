"""
Views for the app.
"""
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status 
from .settings import OPENAI_API_KEY
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from django.shortcuts import render
from django.http import HttpResponse
import json
import pytesseract
from PIL import Image
from .forms import ImageUploadForm

def convert_string_to_json(input_string):
    try:
        # Replace newline characters with spaces
        cleaned_string = input_string.replace('\n', ' ')

        #print(cleaned_string)

        # Load the cleaned string as JSON
        json_data = json.loads(cleaned_string)

        return json_data
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None

class LangchainViewset(viewsets.ModelViewSet):

    @api_view(['POST'])
    def langchain(request):
        question = request.data.get('question')
        if (question):
            question = question
        else:
            question = "Nevermind. Just tell me 'There was no input.'"
        llm = ChatOpenAI(temperature=0.5, openai_api_key=OPENAI_API_KEY)

        messages = [
            SystemMessage(
                content="You are a tool. I want you to split the following into question_number, question_type, questions and options and answers in json format. Ensure to enclose everything in an array. Ignore if a certain type does not exist. "
            ),
            HumanMessage(
                content=question
            ),
        ]

        answer = llm(messages)
        answer_string = answer.content
        print(answer)
        #answer = llm("You are a tool. I want you to split the following into question_number, question_type, questions and options and answers in json format. Ensure to leave as array if there is more than one question. Ignore if a certain type does not exist. "+question)
        
        result = convert_string_to_json(answer_string)
        if result:
            print(json.dumps(result, indent=2))
        else:
            print(answer_string)
            print("JSON conversion failed.")
        return Response({'answer': answer_string})
    
# {
#     "question": "Which of the following aspects of our product/service did you find most impressive? A) Speed and Efficiency B) User-Friendly Interface C) Quality and Reliability D) Customer Support E) Pricing and Value for Money.; Do you feel comfortable asking for help when you’re stuck? A. Yes, I feel very much comfortable asking for help. That’s how you learn! B. No, I’m scared people might judge me."
#     }

@api_view(['POST'])
def upload_image(request):
    form = ImageUploadForm(request.POST, request.FILES)
    
    if form.is_valid():
        uploaded_image = form.cleaned_data['image']

        # Process the uploaded image using PIL and pytesseract
        img = Image.open(uploaded_image)
        ocr_result = pytesseract.image_to_string(img)

        return Response({'deciphered_text': ocr_result})

    return Response({'error': 'Invalid image or OCR processing failed'}, status=status.HTTP_400_BAD_REQUEST)
