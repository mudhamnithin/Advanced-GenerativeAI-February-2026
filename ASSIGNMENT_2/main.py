from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional, List

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

feedback = []

@app.get("/products")
def show_products():
    return {"products": products, "total": len(products)}

@app.get("/products/category/{category_name}")
def category_products(category_name: str):
    data = []
    for p in products:
        if p["category"].lower() == category_name.lower():
            data.append(p)
    if len(data) == 0:
        return {"error": "No products found"}
    return {"products": data}

@app.get("/products/instock")
def available_products():
    data = []
    for p in products:
        if p["in_stock"]:
            data.append(p)
    return {"in_stock_products": data, "count": len(data)}

@app.get("/products/search/{keyword}")
def search_items(keyword: str):
    data = []
    for p in products:
        if keyword.lower() in p["name"].lower():
            data.append(p)
    if len(data) == 0:
        return {"message": "No products matched"}
    return {"matched_products": data, "count": len(data)}

@app.get("/products/filter")
def price_filter(min_value: int):
    data = []
    for p in products:
        if p["price"] >= min_value:
            data.append(p)
    return {"products": data, "count": len(data)}

@app.get("/products/{product_id}/price")
def product_price(product_id: int):
    for p in products:
        if p["id"] == product_id:
            return {"name": p["name"], "price": p["price"]}
    return {"error": "Product not found"}

class CustomerFeedback(BaseModel):
    customer_name: str = Field(..., min_length=2)
    product_id: int = Field(..., gt=0)
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=300)

@app.post("/feedback")
def submit_feedback(data: CustomerFeedback):
    feedback.append(data.dict())
    return {
        "message": "Feedback submitted successfully",
        "feedback": data,
        "total_feedback": len(feedback)
    }

@app.get("/products/summary")
def summary():
    total = len(products)
    instock = 0
    for p in products:
        if p["in_stock"]:
            instock += 1

    outstock = total - instock

    max_item = max(products, key=lambda x: x["price"])
    min_item = min(products, key=lambda x: x["price"])

    cats = []
    for p in products:
        if p["category"] not in cats:
            cats.append(p["category"])

    return {
        "total_products": total,
        "in_stock_count": instock,
        "out_of_stock_count": outstock,
        "most_expensive": {"name": max_item["name"], "price": max_item["price"]},
        "cheapest": {"name": min_item["name"], "price": min_item["price"]},
        "categories": cats
    }

class OrderItem(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., ge=1, le=50)

class BulkOrder(BaseModel):
    company_name: str = Field(..., min_length=2)
    contact_email: str = Field(..., min_length=5)
    items: List[OrderItem]

@app.post("/orders/bulk")
def place_bulk_order(order: BulkOrder):

    success = []
    failed = []
    total_price = 0

    for item in order.items:

        selected = None
        for p in products:
            if p["id"] == item.product_id:
                selected = p
                break

        if selected is None:
            failed.append({"product_id": item.product_id, "reason": "Product not found"})
            continue

        if not selected["in_stock"]:
            failed.append({"product_id": item.product_id, "reason": selected["name"] + " is out of stock"})
            continue

        cost = selected["price"] * item.quantity
        total_price += cost

        success.append({
            "product": selected["name"],
            "qty": item.quantity,
            "subtotal": cost
        })

    return {
        "company": order.company_name,
        "confirmed": success,
        "failed": failed,
        "grand_total": total_price
    }