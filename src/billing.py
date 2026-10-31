def generate_invoice(amount: float, tax_rate: float, currency: str = "INR") -> dict:
    """Calculates final invoice total with tax."""
    total = amount + (amount * tax_rate)
    return {"total": round(total, 2), "currency": currency}
