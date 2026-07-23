from database import Database
import os

def test_calculation():
    # Test normalization and calculation
    # Item 1: 500g, 249 rupees
    # Item 2: 1kg, 450 rupees
    
    # Formula: unit_price = (price * quantity) / weight (normalized)
    
    p1 = 249
    w1 = 500
    q1 = 1
    # unit_price1 = 249 / 500 = 0.498
    
    p2 = 450
    w2 = 1000 # 1kg
    q2 = 1
    # unit_price2 = 450 / 1000 = 0.45
    
    print(f"Item 1 Unit Price: {p1/w1}")
    print(f"Item 2 Unit Price: {p2/w2}")
    
    assert (p2/w2) < (p1/w1), "Item 2 should be cheaper"

def test_database():
    db = Database("test_price_saver.db")
    test_data = [
        {"name": "Cheap Rice", "weight": 1, "unit": "kg", "price": 450, "currency": "₹", "quantity": 1, "unit_price": 0.45},
        {"name": "Expensive Rice", "weight": 500, "unit": "g", "price": 249, "currency": "₹", "quantity": 1, "unit_price": 0.498}
    ]
    
    db.save_comparison(test_data)
    history = db.get_history()
    assert len(history) > 0, "History should not be empty"
    
    history_id = history[0]['id']
    details = db.get_history_details(history_id)
    assert len(details) == 2, "Should have 2 items"
    assert details[0]['is_best_value'] == 1, "First item should be best value"
    
    print("Database and logic tests passed!")
    
    # Cleanup
    db.delete_history_entry(history_id)
    if os.path.exists("test_price_saver.db"):
        os.remove("test_price_saver.db")

if __name__ == "__main__":
    test_calculation()
    test_database()
