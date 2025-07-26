import numpy as np
import random 
from .rag import get_relevant_recipes
import openai
from .config import OPENAI_API_KEY
import re
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
import json

llm = ChatOpenAI(model="gpt-4", temperature=0.7, api_key=OPENAI_API_KEY)

recipe_prompt = PromptTemplate(
    input_variables=["query"],
    template="""
You are a professional chef. Based on the following user query, generate a recipe.

Requirements:
- The output must be in JSON format.
- Include:
  - "title": the name of the dish
  - "servings": the number of servings
  - "ingredients": a list of ingredients
  - "steps": a list of numbered preparation steps

User query: "{query}"

Respond with only the JSON. Do not include any extra explanation.
"""
)

chain = LLMChain(llm=llm, prompt=recipe_prompt)


def call_llm(user_query):
    print("Calling llm", flush=True)
    result = chain.invoke({"query": user_query})
    print("Done calling llm", flush=True)
    output = result["text"]
    print("LLM output type:", type(output), flush=True)
    print("LLM output value:", output, flush=True)
    try:
        data = json.loads(output)
        return data
    except Exception as e:
        print("Failed to parse LLM output as JSON:", output)
        raise

def scale_ingredients(ingredients, base_servings, target_servings):
    scaled_ingredients = []
    ratio = target_servings/base_servings
    for line in ingredients:
        match = re.match(r"(\d*\.?\d+)\s*(.*)", line)
        if match:
            amount = float(match.group(1))
            new_amount = np.round(amount * ratio, 2)
            scaled_ingredients.append(f"{new_amount} {match.group(2)}")
        else:
            scaled_ingredients.append(line)
    return scaled_ingredients

def generate_recipe(query, servings):
    print("Query:", query, flush=True)
    docs = get_relevant_recipes(query, 3)
    if not docs: return None
    doc = docs[random.randint(0, len(docs)-1)]
    result = call_llm(doc)
    print("Query result:", result, flush=True)

    try:
        base_servings = int(result.get("servings",4))
    except:
        base_servings = 4

    scaled_ingredients = scale_ingredients(
        result['ingredients'],
        base_servings,
        servings
    )

    ingredient_str = "\n".join(scaled_ingredients)

    steps = result.get("steps", "")
    if isinstance(steps, list):
        steps_str = "\n".join(steps)
    else:
        steps_str = steps

    title = str(result.get("title", doc.metadata.get("source", "Recipe")))

    formattedResult = {
        "title":title ,
        "ingredients": ingredient_str,
        "steps": steps_str
    }

    print("Formatted Result:", formattedResult, flush=True)

    return formattedResult

def experimental_recipe(servings):
    docs = get_relevant_recipes("ground beef", 12)
    if not docs: return None
    doc = docs[random.randint(0,len(docs)-1)]
    result = call_llm(doc)
    print("Query result:", result, flush=True)

    try:
        base_servings = int(result.get("servings",4))
    except:
        base_servings = 4
    
    
    scaled_ingredients = scale_ingredients(
        result['ingredients'],
        base_servings,
        servings
    )

    ingredient_str = "\n".join(scaled_ingredients)

    steps = result.get("steps", "")
    if isinstance(steps, list):
        steps_str = "\n".join(steps)
    else:
        steps_str = steps

    title = str(result.get("title", doc.metadata.get("source", "Recipe")))

    formattedResult = {
        "title":title ,
        "ingredients": ingredient_str,
        "steps": steps_str
    }

    print("Formatted Result:", formattedResult, flush=True)

    return formattedResult