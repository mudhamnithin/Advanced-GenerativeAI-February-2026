from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional, List

app = FastAPI()

products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True}
]

feedback = []
cart = []
orders = []
order_counter = 1



@app.get("/products")
def get_products():
    return {"products": products, "total": len(products)}


@app.get("/products/category/{category_name}")
def products_by_category(category_name: str):

    result = []

    for p in products:
        if p["category"].lower() == category_name.lower():
            result.append(p)

    if len(result) == 0:
        return {"error": "No products found"}

    return {"products": result}


@app.get("/products/instock")
def instock_products():

    data = []

    for p in products:
        if p["in_stock"]:
            data.append(p)

    return {"in_stock_products": data, "count": len(data)}


@app.get("/products/search/{keyword}")
def search_products(keyword: str):

    result = []

    for p in products:
        if keyword.lower() in p["name"].lower():
            result.append(p)

    if len(result) == 0:
        return {"message": "No products matched"}

    return {"matched_products": result, "count": len(result)}


@app.get("/products/filter")
def filter_products(min_value: int):

    result = []

    for p in products:
        if p["price"] >= min_value:
            result.append(p)

    return {"products": result, "count": len(result)}


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
def add_feedback(data: CustomerFeedback):

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

    expensive = max(products, key=lambda x: x["price"])
    cheap = min(products, key=lambda x: x["price"])

    categories = []

    for p in products:
        if p["category"] not in categories:
            categories.append(p["category"])

    return {
        "total_products": total,
        "in_stock_count": instock,
        "out_of_stock_count": outstock,
        "most_expensive": {"name": expensive["name"], "price": expensive["price"]},
        "cheapest": {"name": cheap["name"], "price": cheap["price"]},
        "categories": categories
    }



class NewProduct(BaseModel):
    name: str
    price: int
    category: str
    in_stock: bool


@app.post("/products")
def add_product(item: NewProduct):

    for p in products:
        if p["name"].lower() == item.name.lower():
            return {"error": "Product already exists"}

    new_id = len(products) + 1

    new_product = {
        "id": new_id,
        "name": item.name,
        "price": item.price,
        "category": item.category,
        "in_stock": item.in_stock
    }

    products.append(new_product)

    return {"message": "Product added", "product": new_product}


@app.put("/products/{product_id}")
def update_product(product_id: int, price: int = None, in_stock: bool = None):

    for p in products:

        if p["id"] == product_id:

            if price is not None:
                p["price"] = price

            if in_stock is not None:
                p["in_stock"] = in_stock

            return {"message": "Product updated", "product": p}

    return {"error": "Product not found"}


@app.delete("/products/{product_id}")
def delete_product(product_id: int):

    for p in products:

        if p["id"] == product_id:
            products.remove(p)
            return {"message": f"Product '{p['name']}' deleted"}

    return {"error": "Product not found"}



@app.post("/cart/add")
def add_to_cart(product_id: int, quantity: int = 1):

    product = None

    for p in products:
        if p["id"] == product_id:
            product = p

    if product is None:
        return {"detail": "Product not found"}

    if not product["in_stock"]:
        return {"detail": f"{product['name']} is out of stock"}

    for item in cart:

        if item["product_id"] == product_id:
            item["quantity"] += quantity
            item["subtotal"] = item["quantity"] * item["unit_price"]

            return {"message": "Cart updated", "cart_item": item}

    cart_item = {
        "product_id": product_id,
        "product_name": product["name"],
        "quantity": quantity,
        "unit_price": product["price"],
        "subtotal": product["price"] * quantity
    }

    cart.append(cart_item)

    return {"message": "Added to cart", "cart_item": cart_item}


@app.get("/cart")
def view_cart():

    if len(cart) == 0:
        return {"message": "Cart is empty"}

    total = 0

    for c in cart:
        total += c["subtotal"]

    return {"items": cart, "item_count": len(cart), "grand_total": total}


@app.delete("/cart/{product_id}")
def remove_from_cart(product_id: int):

    for c in cart:

        if c["product_id"] == product_id:
            cart.remove(c)
            return {"message": f"{c['product_name']} removed"}

    return {"error": "Item not found in cart"}


class Checkout(BaseModel):
    customer_name: str = Field(..., min_length=2)
    delivery_address: str = Field(..., min_length=10)


@app.post("/cart/checkout")
def checkout(data: Checkout):

    global order_counter

    if len(cart) == 0:
        return {"error": "CART_EMPTY"}

    placed = []
    total = 0

    for c in cart:

        order = {
            "order_id": order_counter,
            "customer_name": data.customer_name,
            "product": c["product_name"],
            "quantity": c["quantity"],
            "amount": c["subtotal"]
        }

        orders.append(order)
        placed.append(order)

        total += c["subtotal"]

        order_counter += 1

    cart.clear()

    return {"orders_placed": placed, "grand_total": total}


@app.get("/orders")
def get_orders():

    return {"orders": orders, "total_orders": len(orders)}