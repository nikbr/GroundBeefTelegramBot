from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from app.recipe_tools import (
    generate_recipe, experimental_recipe
)  
import os

load_dotenv(".env")

mcp = FastMCP(
    name="GroundBeefRAGChef",
    host="0.0.0.0",
    port=8050,
)

@mcp.tool()
def create_recipe(dish:str, servings:int) -> dict:
    recipe=generate_recipe(dish, servings)
    if recipe:
        return recipe
    else:
        return {"error": "No recipe found for your input."}
    
@mcp.tool()
def experimental(servings: int) -> dict:
    recipe = experimental_recipe(servings)
    if recipe:
        return recipe
    else:
        return {"error": "No experimental recipe available."}
    
if __name__ == "__main__":
    print("Running MCP server with SSE transport")
    mcp.run(transport="sse")