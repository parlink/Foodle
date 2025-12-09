from django.shortcuts import render
import openai
from openai import OpenAI
from dotenv import load_dotenv
from django.http.response import StreamingHttpResponse
from django.shortcuts import redirect
from recipes.models import Recipe

import os

load_dotenv()


#recipes = []


client = OpenAI(api_key= os.getenv("OPEN_API_KEY"))

def chatbot(request):
   chatbot_response = None
   recipes = request.session.get("recipes",[])

   if request.method == 'POST':
          
          if "clear_history" in request.POST:
               request.session["recipes"] = []
               return redirect ("ai_recipe")

          if "submit" in request.POST:

               user_input = request.POST.get("user_input")
               request.session["last_ingredients"] = user_input



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

                    Mention all of the ingredients needed right after the final step

                    Also add the nutrition info at the end very briefly though.
                    So like Calories: ___, Carbs: ___ etc. Put them all on one line


               so in summary they layout be, recipe name \n 
               step 1 \n
               step 2 \n
               until all of the steps are done """
               },
               {"role":"user", "content":examplePrompt}])

               chatbot_response = response.choices[0].message.content
               chatbot_response = chatbot_response.replace("*","").strip()
               invalid_chars = "@(){}[]<>%^&*$#"
               for ch in invalid_chars:
                    chatbot_response = chatbot_response.replace(ch, "")


               instructions = chatbot_response.split("\n")
               instructions = [line.strip().strip("*") for line in instructions if line.strip()]



               invalid_words = ["invalid","cannot","invaild","can't","isn't enough","cannot create","not enough","doesn't make sense"]

               if any(word in chatbot_response.lower() for word in invalid_words):

                    recipes.append({"type":"invalid","text":chatbot_response})
                    request.session["recipes"] = recipes
                    return redirect("ai_recipe")



               nutrition_index = None
               for i,line in enumerate(instructions):
                   if "nutrition" in line or "calories" in line:
                       nutrition_index = i
                       break

               if nutrition_index is not None:
                    nutrition_block= " ".join(instructions[nutrition_index:])
                    instructions = instructions[:nutrition_index] + [nutrition_block]


               recipes.append({"type":"recipe","steps":instructions})
               request.session["recipes"] = recipes
               return redirect("ai_recipe")











          if "save_recipe" in request.POST:
               index = int(request.POST.get("save_recipe"))
               recipe_to_save  = recipes[index]["steps"]

               title = recipe_to_save[0]
               method = "\n".join(recipe_to_save[1:-1])
               nutrition = recipe_to_save[-1]

               if Recipe.objects.filter(name=title).exists():
                    return redirect("ai_recipe")
               
               placeholder = "images/ai_default_recipes.jpg"

               Recipe.objects.create(
               name = title,
               method = method + "\n\n" + nutrition,
               ingredients = request.session.get("last_ingredients", "AI ingredients"),
               total_time = "N/A",
               servings = 1,
               difficulty = "Easy",
               average_rating = 0


               )

               return redirect("ai_recipe")



        
   return render(request,"AI_recipe.html",{"recipes": recipes})

