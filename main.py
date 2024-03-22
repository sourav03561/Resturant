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
from datetime import time, datetime

app = FastAPI()

restaurants = []


@app.get("/print_all_menu/")
async def print_all_menu():
        # Reference to the User collection
        # List to store all menu items for each restaurant
        user_ref = db.collection(u'User')
        docs = user_ref.stream()
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
    user_ref = db.collection(u'User')
    docs = user_ref.stream()
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
        user_ref = db.collection(u'User')
        docs = user_ref.stream()
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
    user_ref = db.collection(u'User')
    docs = user_ref.stream()
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
# Feature 4: get opening and closing time of a particular resturant
@app.get("/restaurant/timing/{restaurant_name}")
async def get_restaurant_timing(restaurant_name: str):
    user_ref = db.collection(u'User')
    query = user_ref.where(u'name', u'==', restaurant_name)
    docs = query.stream()

    for doc in docs:
        restaurant_data = doc.to_dict()
        opening_time_str = restaurant_data.get("opening_time")
        closing_time_str = restaurant_data.get("closing_time")
        
        # Convert opening_time and closing_time to time objects
        opening_time = datetime.strptime(opening_time_str, "%H:%M").time() if opening_time_str else None
        closing_time = datetime.strptime(closing_time_str, "%H:%M").time() if closing_time_str else None
        
        return {
            "restaurant_name": restaurant_name,
            "opening_time": opening_time.strftime("%H:%M") if opening_time else "N/A",
            "closing_time": closing_time.strftime("%H:%M") if closing_time else "N/A"
        }
    
    return {"message": "Restaurant not found"}
# feature 5: get resturant by category
@app.get("/restaurants/")
async def get_restaurants_by_category(category: str):
    user_ref = db.collection(u'User')
    query = user_ref.where(u'category', u'==', category)
    docs = query.stream()
    
    restaurants = []
    for doc in docs:
        restaurant_data = doc.to_dict()
        restaurants.append({
            "name": restaurant_data.get("name"),
            "menu": restaurant_data.get("menu"),
            "category": restaurant_data.get("category")
        })
    
    return restaurants
        
# Endpoint to add a new restaurant
# done
@app.post("/restaurant/add/")
async def add_restaurant(restaurant_data: Dict[str, Any]):
    user_ref = db.collection(u'User')
    docs = user_ref.stream()
    restaurants.append(restaurant_data)
    for record in restaurants:
        doc_ref = db.collection(u'User').document(record['name'])
        doc_ref.set(record)
    return {"message": "Restaurant added successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
