from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional, List

app = FastAPI()

items_db = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True}
]

reviews = []
cart_box = []
orders_db = []
order_id = 1


@app.get("/products")
def list_all():
    return {"products": items_db, "total": len(items_db)}


@app.get("/products/category/{cat}")
def by_category(cat: str):
    res = []
    for x in items_db:
        if x["category"].lower() == cat.lower():
            res.append(x)
    if len(res) == 0:
        return {"error": "No products found"}
    return {"products": res}


@app.get("/products/instock")
def stock_items():
    res = []
    for x in items_db:
        if x["in_stock"]:
            res.append(x)
    return {"in_stock_products": res, "count": len(res)}


@app.get("/products/search/{key}")
def search_item(key: str):
    res = []
    for x in items_db:
        if key.lower() in x["name"].lower():
            res.append(x)
    if len(res) == 0:
        return {"message": "No products matched"}
    return {"matched_products": res, "count": len(res)}


@app.get("/products/filter")
def filter_price(min_price: int):
    res = []
    for x in items_db:
        if x["price"] >= min_price:
            res.append(x)
    return {"products": res, "count": len(res)}


@app.get("/products/{pid}/price")
def price_view(pid: int):
    for x in items_db:
        if x["id"] == pid:
            return {"name": x["name"], "price": x["price"]}
    return {"error": "Product not found"}


class Feed(BaseModel):
    customer_name: str = Field(..., min_length=2)
    product_id: int = Field(..., gt=0)
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=300)


@app.post("/feedback")
def save_feedback(data: Feed):
    reviews.append(data.dict())
    return {
        "message": "Feedback submitted successfully",
        "feedback": data,
        "total_feedback": len(reviews)
    }


@app.get("/products/summary")
def summary_view():
    total = len(items_db)
    instock = 0
    for x in items_db:
        if x["in_stock"]:
            instock += 1
    out = total - instock
    high = max(items_db, key=lambda x: x["price"])
    low = min(items_db, key=lambda x: x["price"])
    cats = []
    for x in items_db:
        if x["category"] not in cats:
            cats.append(x["category"])
    return {
        "total_products": total,
        "in_stock_count": instock,
        "out_of_stock_count": out,
        "most_expensive": {"name": high["name"], "price": high["price"]},
        "cheapest": {"name": low["name"], "price": low["price"]},
        "categories": cats
    }


class NewItem(BaseModel):
    name: str
    price: int
    category: str
    in_stock: bool


@app.post("/products")
def add_item(data: NewItem):
    for x in items_db:
        if x["name"].lower() == data.name.lower():
            return {"error": "Product already exists"}
    new_id = len(items_db) + 1
    obj = {
        "id": new_id,
        "name": data.name,
        "price": data.price,
        "category": data.category,
        "in_stock": data.in_stock
    }
    items_db.append(obj)
    return {"message": "Product added", "product": obj}


@app.put("/products/{pid}")
def update_item(pid: int, price: int = None, in_stock: bool = None):
    for x in items_db:
        if x["id"] == pid:
            if price is not None:
                x["price"] = price
            if in_stock is not None:
                x["in_stock"] = in_stock
            return {"message": "Product updated", "product": x}
    return {"error": "Product not found"}


@app.delete("/products/{pid}")
def delete_item(pid: int):
    for x in items_db:
        if x["id"] == pid:
            items_db.remove(x)
            return {"message": f"Product '{x['name']}' deleted"}
    return {"error": "Product not found"}


class OrderUnit(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., ge=1, le=50)


class Bulk(BaseModel):
    company_name: str = Field(..., min_length=2)
    contact_email: str = Field(..., min_length=5)
    items: List[OrderUnit]


@app.post("/orders/bulk")
def bulk_order(data: Bulk):
    ok = []
    bad = []
    total = 0

    for i in data.items:
        prod = None
        for x in items_db:
            if x["id"] == i.product_id:
                prod = x
                break

        if prod is None:
            bad.append({"product_id": i.product_id, "reason": "Product not found"})
            continue

        if not prod["in_stock"]:
            bad.append({"product_id": i.product_id, "reason": prod["name"] + " is out of stock"})
            continue

        cost = prod["price"] * i.quantity
        total += cost

        ok.append({
            "product": prod["name"],
            "qty": i.quantity,
            "subtotal": cost
        })

    return {
        "company": data.company_name,
        "confirmed": ok,
        "failed": bad,
        "grand_total": total
    }


@app.post("/cart/add")
def add_cart(product_id: int, quantity: int = 1):

    prod = None
    for x in items_db:
        if x["id"] == product_id:
            prod = x

    if prod is None:
        return {"detail": "Product not found"}

    if not prod["in_stock"]:
        return {"detail": f"{prod['name']} is out of stock"}

    for c in cart_box:
        if c["product_id"] == product_id:
            c["quantity"] += quantity
            c["subtotal"] = c["quantity"] * c["unit_price"]
            return {"message": "Cart updated", "cart_item": c}

    new = {
        "product_id": product_id,
        "product_name": prod["name"],
        "quantity": quantity,
        "unit_price": prod["price"],
        "subtotal": prod["price"] * quantity
    }

    cart_box.append(new)

    return {"message": "Added to cart", "cart_item": new}


@app.get("/cart")
def view_cart():
    if len(cart_box) == 0:
        return {"message": "Cart is empty"}
    total = 0
    for c in cart_box:
        total += c["subtotal"]
    return {"items": cart_box, "item_count": len(cart_box), "grand_total": total}


@app.delete("/cart/{pid}")
def remove_cart(pid: int):
    for c in cart_box:
        if c["product_id"] == pid:
            cart_box.remove(c)
            return {"message": f"{c['product_name']} removed"}
    return {"error": "Item not found"}


class Checkout(BaseModel):
    customer_name: str = Field(..., min_length=2)
    delivery_address: str = Field(..., min_length=10)


@app.post("/cart/checkout")
def checkout(data: Checkout):
    global order_id

    if len(cart_box) == 0:
        return {"error": "CART_EMPTY"}

    result = []
    total = 0

    for c in cart_box:
        order = {
            "order_id": order_id,
            "customer_name": data.customer_name,
            "product": c["product_name"],
            "quantity": c["quantity"],
            "amount": c["subtotal"]
        }
        orders_db.append(order)
        result.append(order)
        total += c["subtotal"]
        order_id += 1

    cart_box.clear()

    return {"orders_placed": result, "grand_total": total}


@app.get("/orders")
def show_orders():
    return {"orders": orders_db, "total_orders": len(orders_db)}