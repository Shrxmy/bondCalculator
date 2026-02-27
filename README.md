# Bond Pricing Calculator

A professional bond pricing and yield curve analysis tool built with Python and Streamlit.

## Features

### Price Calculator
- **Dirty Price** and **Clean Price** computation
- **Accrued Interest** with configurable day-count conventions
- **Macaulay Duration** and **Modified Duration**
- **Convexity** measurement
- Supports multiple coupon frequencies: annually, semi-annually, quarterly, monthly
- Day-count conventions: 30/360, Actual/360, Actual/365, Actual/Actual

### Curve Analysis
- Bootstrap zero-coupon **spot rates** from par yields
- Compute **implied forward rates** between maturities
- Interactive rate curve chart (Par Yield vs. Spot Rate)

---

## Prerequisites

- **Python 3.10+** — [Download here](https://www.python.org/downloads/)
- **pip** (included with Python)

---

## Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/<your-username>/bondCalculator.git
   cd bondCalculator
   ```

2. **Create a virtual environment** (recommended)

   ```bash
   python -m venv .venv
   ```

   Activate it:

   | OS      | Command                        |
   |---------|--------------------------------|
   | Windows | `.venv\Scripts\activate`       |
   | macOS / Linux | `source .venv/bin/activate` |

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

---

## Running the App

```bash
streamlit run app.py
```

The app will open automatically in your default browser at **http://localhost:8501**.

---

## Project Structure

```
bondCalculator/
├── app.py              # Streamlit UI (Price Calculator & Curve Analysis tabs)
├── bond_calc.py        # Core bond math (pricing, duration, convexity, bootstrapping)
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

---

## Usage

### Price Calculator

1. Enter the bond's **Face Value**, **Yield (%)**, and **Coupon (%)**.
2. Select the **Coupon Frequency** and **Day-count Convention**.
3. Set the **Maturity Date** and **Settlement Date**.
4. Click **Calculate Price** to view results.

### Curve Analysis

1. Edit the **Par Yield** table with current market rates for each maturity.
2. Click **Analyze Curve** to see bootstrapped spot rates, implied forward rates, and the rate curve chart.

---

## License

This project is provided as-is for educational and personal use.
