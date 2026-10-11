def price(items, tax_bps):
    subtotal = sum(item["price"] * item["quantity"] for item in items)
    tax = (subtotal * tax_bps + 5000) // 10000
    return {"subtotal": subtotal, "tax": tax, "total": subtotal + tax}
