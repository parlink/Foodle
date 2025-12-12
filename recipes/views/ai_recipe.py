from django.shortcuts import render, redirect
from django.conf import settings
from openai import OpenAI
from django.contrib import messages


#recipes = []


def chatbot(request):
   chatbot_response = None
   
   recipes = request.session.get("recipes",[])

   if request.method == 'POST':
        if "submit" in request.POST:
            
          user_input = request.POST.get("user_input")


          examplePrompt = f"""     
          Ingredients: Chicken and Rice
          Steps
          1. Cook rice
          2. Add Chicken

          Ingredients: Eggs and Cheese
          Steps
          1. Beat Eggs
          2. Add Cheese

          Ingredients: {user_input} 
          Recipe Title:
          """





          api_key = getattr(settings, 'OPENAI_API_KEY', None)
          if not api_key:
              messages.error(request, 'OpenAI API key is not configured. Please contact the administrator.')
              return redirect('ai_recipes')
          
          try:
              client = OpenAI(api_key=api_key)
              response = client.chat.completions.create(
                   model = "gpt-4o",
                   messages = [{"role": "system",
                                 "content" : """You are a helpful chef, your job is to 
                   give a recipe name and give the  user brief instructions on how to make it
                   make it line by line. If it is invalid then say it's invalid
                   each instruction that you write should be on a new line
                   Put each instruction on a separate line pls.
                   If there is not one valid ingredient, then reply with something like
                   this is an invalid ingredient etc etc, and DONT make a recipe for it
                   don't say invalid to every thing that can't be made
                   if they missed out some instructions then perhaps add some of your own
                   but obv don't add too many or make it into some crazy dish
                   then at the end you could briefly say, I have added these ingredients ...
                   but only do that if they only put in like a couple items and you literally
                   can't make anything with those

                   If an ingredient is not appropriate with the rest of the ingredients then do not 
                   include it in the recipe since it will not match.


                   so in summary they layout be, recipe name \n 
                   step 1 \n
                   step 2 \n
                   until all of the steps are done """
                   },
                   {"role":"user", "content":examplePrompt}])

              chatbot_response = response.choices[0].message.content
              instructions = chatbot_response.split("\n")
              recipes.append(instructions)
              request.session["recipes"] = recipes
              return redirect('ai_recipes')
          except Exception as e:
              messages.error(request, f'Error generating recipe: {str(e)}')
              return redirect('ai_recipes')


        if "clear_history" in request.POST:
           request.session["recipes"] = []
           recipes = []
            
     
          
       

       # request.session = {"recipes" : chatbot_response}
       
        
   return render(request,"AI_Recipe.html",{"recipes": recipes})
