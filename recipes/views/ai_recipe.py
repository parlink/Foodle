from django.shortcuts import render
import openai, os
from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()
OPEN_API_KEY = os.getenv("OPEN_API_KEY")


openai.api_key = OPEN_API_KEY




#client = OpenAI(api_key=OPEN_API_KEY)

def chatbot(request):
    chatbot_response = None
    if (request.method == 'POST'):
        openai.api_key = OPEN_API_KEY
        user_input = request.POST.get("user_input")
        

        response = openai.completions.create(
            engine = 'text-davinci-003',
            prompt=user_input,
            max_tokens=256, 
            stop = ".",
            temperature= 0.5,
            

        )

    return render(request,"AI_recipe.html",{"response" : chatbot_response})

