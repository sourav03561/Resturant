from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials

cred = credentials.Certificate("bubai-23f98-firebase-adminsdk-52ihc-be28227dd4.json")
firebase_admin.initialize_app(cred)
db = firestore.client()
from fastapi import FastAPI, Query
from typing import List, Dict, Any

app = FastAPI()

restaurants = []

user_ref = db.collection(u'User')
docs = user_ref.stream()

@app.get("/print_all_menu/")
async def print_all_menu():
        # Reference to the User collection
        # List to store all menu items for each restaurant
        all_menu = []

        # Iterate over documents and add menu items to the list
        for doc in docs:
            restaurant_data = doc.to_dict()
            menu = restaurant_data.get("menu", [])
            restaurant_menu = {
                "restaurant_name": restaurant_data.get("name", ""),
                "menu": menu
            }
            all_menu.append(restaurant_menu)

        return all_menu

# Feature 1: Search by Restaurants to Get Menu
# done
@app.get("/restaurant/menu/{restaurant_name}")
async def get_menu(restaurant_name: str):
    for restaurant in docs:
        restaurant_data = restaurant.to_dict()
        if restaurant_data.get("name") == restaurant_name:
            return restaurant_data.get("menu")
    return {"message": "Restaurant not found"}

#feature 2 search dish with 
# done 
@app.get("/dish/search/")
async def search_dish(dish_name: str = Query(..., title="Dish Name")):
    try:
        results = []
        for doc in docs:
            restaurant = doc.to_dict()
            menu = restaurant.get("menu", [])
            for dish in menu:
                if dish.get("name") == dish_name:
                    results.append({
                        "restaurant": restaurant.get("name", ""),
                        "price": dish.get("price", "")
                    })
        return results

    except Exception as e:
        return {"error": str(e)}

# Feature 3: Best Restaurants within a Particular Radius of Current Location Sorted by Rating
# done
@app.get("/restaurants/best/")
async def best_restaurants(latitude: float = Query(...), longitude: float = Query(...), radius: float = Query(10)):
    results = []
    for restaurant in docs:
        # Simple distance calculation, assuming coordinates are in degrees
        restaurant_data = restaurant.to_dict()
        distance = ((restaurant_data["cord"][0] - latitude) ** 2 + (restaurant_data["cord"][1] - longitude) ** 2) ** 0.5
        if distance <= radius:
            results.append({
                "name": restaurant_data.get("name", ""),
                "rating": restaurant_data.get("rating", ""),
                "distance": distance
            })
    results.sort(key=lambda x: x["rating"], reverse=True)
    return results


# Endpoint to add a new restaurant
# done
@app.post("/restaurant/add/")
async def add_restaurant(restaurant_data: Dict[str, Any]):
    restaurants.append(restaurant_data)
    for record in restaurants:
        doc_ref = db.collection(u'User').document(record['name'])
        doc_ref.set(record)
    return {"message": "Restaurant added successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
