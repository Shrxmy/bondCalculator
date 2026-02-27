import datetime
from dataclasses import dataclass
from typing import Literal
import math

DayCountConvention = Literal["30/360", "Actual/360", "Actual/365", "Actual/Actual"]
Frequency = Literal["annually", "semi-annually", "quarterly", "monthly"]

@dataclass
class Bond:
    face_value: float
    yield_rate: float  # as percentage, e.g. 6.0
    coupon_rate: float # as percentage, e.g. 5.0
    frequency: Frequency
    maturity_date: datetime.date
    settlement_date: datetime.date
    convention: DayCountConvention

    def _get_frequency_int(self) -> int:
        if self.frequency == "annually": return 1
        if self.frequency == "semi-annually": return 2
        if self.frequency == "quarterly": return 4
        if self.frequency == "monthly": return 12
        return 1

    def _calculate_days_30360(self, d1: datetime.date, d2: datetime.date) -> int:
        d1_day = d1.day
        d2_day = d2.day
        d1_month = d1.month
        d2_month = d2.month
        d1_year = d1.year
        d2_year = d2.year

        if d1_day == 31:
            d1_day = 30
        if d2_day == 31 and d1_day == 30:
            d2_day = 30
            
        return 360 * (d2_year - d1_year) + 30 * (d2_month - d1_month) + (d2_day - d1_day)

    def _calculate_year_fraction(self, d1: datetime.date, d2: datetime.date) -> float:
        if self.convention == "30/360":
            days = self._calculate_days_30360(d1, d2)
            return days / 360.0
        elif self.convention == "Actual/360":
            days = (d2 - d1).days
            return days / 360.0
        elif self.convention == "Actual/365":
            days = (d2 - d1).days
            return days / 365.0
        elif self.convention == "Actual/Actual":
            # Simplification: Actual/Actual ISDA
            days = (d2 - d1).days
            # Check for leap year handling if spanning years, but for simple pricing often diff/365.25 or similar
            # For strict ISDA:
            y1 = d1.year
            y2 = d2.year
            if y1 == y2:
                days_in_year = 366 if (y1 % 4 == 0 and (y1 % 100 != 0 or y1 % 400 == 0)) else 365
                return days / days_in_year
            else:
                # This is a complex calculation, using a reasonable approximation for now or basic Act/365
                # Reverting to Act/365 for simplicity unless precise ISDA is needed, 
                # but let's try to be slightly better:
                return days / 365.25 
        return 0.0
    
    def _is_coupon_date(self, date: datetime.date) -> bool:
        # Simplistic check assuming maturity date sets the cycle
        # TODO: Handle detailed day adjustments
        return date.day == self.maturity_date.day and date.month == self.maturity_date.month # Logic incomplete for freq != annual

    def get_last_coupon_date(self) -> datetime.date:
        # Traverse backwards from maturity
        # This is a bit brute force but robust for small differences
        freq = self._get_frequency_int()
        months_step = 12 // freq
        
        current_candidate = self.maturity_date
        while current_candidate > self.settlement_date:
            # Move back one period
            year = current_candidate.year
            month = current_candidate.month - months_step
            while month <= 0:
                month += 12
                year -= 1
            
            # Handle end of month issues generally, but for now assuming valid dates (e.g. 23rd is safe)
            # If 31st, might need adjustment.
            try:
                current_candidate = datetime.date(year, month, current_candidate.day)
            except ValueError:
                # Handle Feb 29 etc.
                if current_candidate.day >= 29:
                    current_candidate = datetime.date(year, month, 28) # Simple fallback
        
        return current_candidate

    def calculate(self):
        freq = self._get_frequency_int()
        coupon_val = self.face_value * (self.coupon_rate / 100.0) / freq
        yield_dec = self.yield_rate / 100.0
        
        # 1. Calculate Accrued Interest
        last_coupon = self.get_last_coupon_date()
        
        # Days for accrued:
        # Note: Denominator bases differ by convention.
        # For 30/360, use 30/360 days.
        if self.convention == "30/360":
            days_accrued = self._calculate_days_30360(last_coupon, self.settlement_date)
            # Annual basis is 360
            accrued_interest = coupon_val * (days_accrued / (360 / freq)) 
            # Note: 360/freq is days in period for 30/360 approx.
        elif self.convention == "Actual/360":
            days_accrued = (self.settlement_date - last_coupon).days
            accrued_interest = coupon_val * (days_accrued / (360 / freq)) # Market convention can vary here
        elif self.convention == "Actual/365":
            days_accrued = (self.settlement_date - last_coupon).days
            accrued_interest = coupon_val * (days_accrued / (365 / freq))
        else: # Actual/Actual
            days_accrued = (self.settlement_date - last_coupon).days
            # Find next coupon for reference period
            # next_c = ...
            # For simplicity, using Act/365 approximation equivalent for now or 
            # standard: accrued = coupon * (days_since_last / days_in_period)
            # Let's find next coupon to get days_in_period accurately
            months_step = 12 // freq
            y_next = last_coupon.year
            m_next = last_coupon.month + months_step
            if m_next > 12:
                m_next -= 12
                y_next += 1
            # Adjust day if needed
            try:
                next_coupon = datetime.date(y_next, m_next, last_coupon.day)
            except:
                 next_coupon = datetime.date(y_next, m_next, 28)
            
            days_in_period = (next_coupon - last_coupon).days
            accrued_interest = coupon_val * (days_accrued / days_in_period)

        # 2. Discount Cash Flows for Dirty Price
        # Generate remaining cash flows
        cash_flows = []
        current_date = last_coupon
        months_step = 12 // freq
        
        # Move to next coupon (first future payment)
        # We need to find the first coupon AFTER settlement
        # Logic in get_last_coupon ensured last_coupon <= settlement
        
        # Advance to first coupon date after last_coupon
        y_next = last_coupon.year
        m_next = last_coupon.month + months_step
        while m_next > 12:
            m_next -= 12
            y_next += 1
        try:
             next_coupon_date = datetime.date(y_next, m_next, last_coupon.day)
        except:
             next_coupon_date = datetime.date(y_next, m_next, 28)

        # Generate all future coupons until maturity
        current_cf_date = next_coupon_date
        while current_cf_date <= self.maturity_date:
            amount = coupon_val
            if current_cf_date == self.maturity_date:
                amount += self.face_value
            
            cash_flows.append((current_cf_date, amount))
            
            # Next date
            y = current_cf_date.year
            m = current_cf_date.month + months_step
            while m > 12:
                m -= 12
                y += 1
            try:
                current_cf_date = datetime.date(y, m, current_cf_date.day)
            except:
                 current_cf_date = datetime.date(y, m, 28)

        # Discounting
        dirty_price = 0.0
        duration_sum = 0.0
        convexity_sum = 0.0
        for cf_date, amount in cash_flows:
            # Time from settlement to cash flow (in years)
            t = self._calculate_year_fraction(self.settlement_date, cf_date)
            
            # Number of periods from settlement
            n = freq * t
            
            # Discount factor: 1 / (1 + yield/freq)^(freq * t)
            discount_factor = 1 / pow(1 + yield_dec/freq, n)
            pv = amount * discount_factor
            dirty_price += pv
            
            # Macaulay duration contribution: t * PV(CF)
            duration_sum += t * pv
            
            # Convexity contribution: CF * n * (n+1) / (1 + y/freq)^(n+2)
            convexity_sum += amount * n * (n + 1) / pow(1 + yield_dec/freq, n + 2)

        clean_price = dirty_price - accrued_interest
        
        # Macaulay Duration = (1/P) * sum[ t * PV(CF) ]
        macaulay_duration = duration_sum / dirty_price if dirty_price != 0 else 0.0
        
        # Modified Duration = Macaulay Duration / (1 + y/freq)
        modified_duration = macaulay_duration / (1 + yield_dec / freq)
        
        # Convexity = (1 / (P * freq^2)) * sum[ CF * n*(n+1) / (1+y/freq)^(n+2) ]
        convexity = convexity_sum / (dirty_price * freq * freq) if dirty_price != 0 else 0.0

        return {
            "dirty_price": dirty_price,
            "clean_price": clean_price,
            "accrued_interest": accrued_interest,
            "days_accrued": days_accrued,
            "macaulay_duration": macaulay_duration,
            "modified_duration": modified_duration,
            "convexity": convexity
        }

def calculate_forward_rate(rate_t1: float, t1: float, rate_t2: float, t2: float) -> float:
    """
    Calculates the implied forward rate between time t1 and t2.
    rate_t1: Zero rate for time t1 (percent)
    rate_t2: Zero rate for time t2 (percent)
    r_forward = [(1+r2)^t2 / (1+r1)^t1]^[1/(t2-t1)] - 1
    """
    if t2 <= t1:
        return 0.0
        
    r1 = rate_t1 / 100.0
    r2 = rate_t2 / 100.0
    
    # Discount factors
    df1 = pow(1 + r1, t1)
    df2 = pow(1 + r2, t2)
    
    forward_factor = df2 / df1
    time_diff = t2 - t1
    
    forward_rate = (pow(forward_factor, 1/time_diff) - 1) * 100.0
    return forward_rate

def bootstrap_spot_curve(par_yields: dict[int, float]) -> dict[int, float]:
    """
    Bootstraps the zero/spot curve from par yields.
    par_yields: dict {year: yield_percent}
    Returns: dict {year: spot_percent}
    """
    sorted_years = sorted(par_yields.keys())
    spot_curve = {}
    
    for year in sorted_years:
        par_yield = par_yields[year] / 100.0
        coupon = 100.0 * par_yield
        
        # PV = Sum(Coupons / (1+z_t)^t) + (100 + Coupon) / (1+z_n)^n = 100
        # For year 1 (simple case if no prior coupons): 100 = (100 + C) / (1 + z1) -> z1 = C
        
        pv_prior_coupons = 0.0
        
        # Calculate PV of coupons paid in years 1 to year-1 using KNOWN spot rates
        for t in range(1, year):
            if t in spot_curve:
                z_t = spot_curve[t] / 100.0
                pv_prior_coupons += coupon / pow(1 + z_t, t)
            else:
                # Missing intermediate point? Linear interpolation or error.
                # Simplification: Assume annual steps available.
                # If gap exists (e.g. 1y, 5y), we need interpolation logic.
                # For this basic implementation, we assume continuous integers or we check gaps.
                pass 
                
        # Remainder of PV must come from final payment (Year n)
        # 100 = PV_prior + (100 + Coupon) / (1 + z_n)^n
        # (100 - PV_prior) = (100 + Coupon) / (1 + z_n)^n
        # (1 + z_n)^n = (100 + Coupon) / (100 - PV_prior)
        
        remaining_val = 100.0 - pv_prior_coupons
        
        # Safety check
        if remaining_val <= 0:
            spot_curve[year] = 0.0 # Mathematical impossibility for normal rates
            continue
            
        final_payment = 100.0 + coupon
        discount_factor_n = remaining_val / final_payment
        # discount_factor_n = 1 / (1+z)^n
        
        # (1+z) = (1/df)^(1/n)
        z_n = pow(1.0 / discount_factor_n, 1.0 / year) - 1.0
        spot_curve[year] = z_n * 100.0
        
    return spot_curve
