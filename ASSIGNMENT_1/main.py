from fastapi import FastAPI

app = FastAPI()

products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": False},
    {"id": 4, "name": "USB Cable", "price": 199, "category": "Electronics", "in_stock": True},

    {"id": 5, "name": "Laptop Stand", "price": 999, "category": "Electronics", "in_stock": True},
    {"id": 6, "name": "Mechanical Keyboard", "price": 2499, "category": "Electronics", "in_stock": True},
    {"id": 7, "name": "Webcam", "price": 1499, "category": "Electronics", "in_stock": False}
]
@app.get("/products")
def get_products():
    return {
        "products": products,
        "total": len(products)
    }
@app.get("/products/category/{category_name}")
def get_category(category_name: str):

    result = []

    for p in products:
        if p["category"].lower() == category_name.lower():
            result.append(p)

    if len(result) == 0:
        return {"error": "No products found in this category"}

    return {"products": result}
@app.get("/products/instock")
def instock_products():

    instock = []

    for p in products:
        if p["in_stock"] == True:
            instock.append(p)

    return {
        "in_stock_products": instock,
        "count": len(instock)
    }
@app.get("/store/summary")
def store_summary():

    total = len(products)

    instock = 0
    for p in products:
        if p["in_stock"]:
            instock += 1

    outstock = total - instock

    categories = []
    for p in products:
        if p["category"] not in categories:
            categories.append(p["category"])

    return {
        "store_name": "My E-commerce Store",
        "total_products": total,
        "in_stock": instock,
        "out_of_stock": outstock,
        "categories": categories
    }
@app.get("/products/search/{keyword}")
def search_product(keyword: str):

    result = []

    for p in products:
        if keyword.lower() in p["name"].lower():
            result.append(p)

    if len(result) == 0:
        return {"message": "No products matched your search"}

    return {
        "matched_products": result,
        "count": len(result)
    }