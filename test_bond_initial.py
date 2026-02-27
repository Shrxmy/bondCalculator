import datetime
from bond_calc import Bond

def test_example():
    # Example from screenshot
    # Face: 100
    # Yield: 6%
    # Annual coupon: 5%
    # Frequency: annually
    # Maturity: 01/23/2029
    # Settlement: 01/27/2026
    # Day-count: 30/360
    
    bond = Bond(
        face_value=100.0,
        yield_rate=6.0,
        coupon_rate=5.0,
        frequency="annually",
        maturity_date=datetime.date(2029, 1, 23),
        settlement_date=datetime.date(2026, 1, 27),
        convention="30/360"
    )
    
    results = bond.calculate()
    
    print("Results:")
    print(f"Dirty Price: {results['dirty_price']:.4f}")
    print(f"Clean Price: {results['clean_price']:.4f}")
    print(f"Accrued Interest: {results['accrued_interest']:.4f}")
    print(f"Days Accrued: {results['days_accrued']}")

if __name__ == "__main__":
    test_example()
