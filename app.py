import streamlit as st
import datetime
import warnings
import pandas as pd
from bond_calc import Bond, bootstrap_spot_curve, calculate_forward_rate

warnings.simplefilter(action='ignore', category=FutureWarning)

st.set_page_config(page_title="Bond Pricing Calculator", layout="wide")

# ── Global CSS ──────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* ---------- page ---------- */
    .block-container { padding-top: 2rem; }

    /* ---------- tabs ---------- */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        border-bottom: 2px solid #e2e8f0;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        color: #64748b;
        border-bottom: 3px solid transparent;
    }
    .stTabs [aria-selected="true"] {
        color: #1e293b;
        border-bottom: 3px solid #2563eb;
    }

    /* ---------- metric cards ---------- */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1rem 1.25rem;
        box-shadow: 0 1px 3px rgba(0,0,0,.06);
        transition: transform .15s ease, box-shadow .15s ease;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,.1);
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748b;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.35rem;
        font-weight: 700;
        color: #0f172a;
    }

    /* ---------- button ---------- */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #2563eb, #1d4ed8);
        color: #fff;
        border: none;
        border-radius: 8px;
        padding: 0.65rem 1.5rem;
        font-weight: 600;
        font-size: 0.95rem;
        letter-spacing: .02em;
        transition: all .2s ease;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #1d4ed8, #1e40af);
        box-shadow: 0 4px 14px rgba(37, 99, 235, .35);
        transform: translateY(-1px);
    }
    .stButton > button:active {
        transform: translateY(0);
    }

    /* ---------- expander ---------- */
    .streamlit-expanderHeader {
        font-weight: 600;
        font-size: 1.05rem;
        color: #1e293b;
    }

    /* ---------- section header ---------- */
    .section-title {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #94a3b8;
        font-weight: 700;
        margin-bottom: 0.25rem;
    }

    /* ---------- result banner ---------- */
    .results-banner {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        color: #fff;
        padding: 0.75rem 1.25rem;
        border-radius: 10px 10px 0 0;
        font-weight: 700;
        font-size: 1rem;
        letter-spacing: .02em;
    }

    /* ---------- data editor / table ---------- */
    .stDataFrame { border-radius: 10px; overflow: hidden; }

    /* ---------- divider ---------- */
    hr { border-color: #e2e8f0 !important; }
</style>
""", unsafe_allow_html=True)

# ── Header ──────────────────────────────────────────────────────────────
st.markdown("## Bond Pricing Calculator")
st.caption("Compute dirty price, clean price, accrued interest, and convexity for bonds settling between coupon dates.")

# ── Tabs ────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["Price Calculator", "Curve Analysis"])

# =====================================================================
#  TAB 1 — PRICE CALCULATOR
# =====================================================================
with tab1:
    col_input, col_spacer, col_output = st.columns([5, 0.5, 5])

    with col_input:
        st.markdown('<p class="section-title">Bond Details</p>', unsafe_allow_html=True)

        face_value = st.number_input("Face value (₱)", min_value=0.0, value=100.0, format="%.2f")

        r1, r2 = st.columns(2)
        with r1:
            yield_rate = st.number_input("Yield (%)", value=6.0, format="%.3f")
        with r2:
            coupon_rate = st.number_input("Coupon (%)", value=5.0, format="%.3f")

        frequency = st.selectbox(
            "Coupon frequency",
            ["annually", "semi-annually", "quarterly", "monthly"],
            index=0,
        )

        d1, d2 = st.columns(2)
        with d1:
            maturity_date = st.date_input("Maturity date", value=datetime.date(2029, 1, 23))
        with d2:
            settlement_date = st.date_input("Settlement date", value=datetime.date(2026, 1, 27))

        convention = st.selectbox(
            "Day-count convention",
            ["30/360", "Actual/360", "Actual/365", "Actual/Actual"],
        )

        st.write("")  # spacer
        calculate = st.button("Calculate Price", use_container_width=True)

    # ── Results column ──
    with col_output:
        if calculate:
            bond = Bond(
                face_value=face_value,
                yield_rate=yield_rate,
                coupon_rate=coupon_rate,
                frequency=frequency,
                maturity_date=maturity_date,
                settlement_date=settlement_date,
                convention=convention,
            )

            try:
                results = bond.calculate()

                st.markdown('<div class="results-banner">Results</div>', unsafe_allow_html=True)
                st.write("")  # small spacer

                m1, m2 = st.columns(2)
                m1.metric("Dirty Price", f"₱ {results['dirty_price']:,.4f}")
                m2.metric("Clean Price", f"₱ {results['clean_price']:,.4f}")

                m3, m4 = st.columns(2)
                m3.metric("Accrued Interest", f"₱ {results['accrued_interest']:,.4f}")
                m4.metric("Accrued Days", f"{results['days_accrued']}")

                st.write("")
                m5, m6 = st.columns(2)
                m5.metric("Macaulay Duration", f"{results['macaulay_duration']:,.4f} yrs")
                m6.metric("Modified Duration", f"{results['modified_duration']:,.4f}")

                m7, _ = st.columns(2)
                m7.metric("Convexity", f"{results['convexity']:,.4f}")

            except Exception as e:
                st.error(f"Calculation error: {e}")
        else:
            st.markdown(
                """
                <div style="
                    display: flex; align-items: center; justify-content: center;
                    height: 340px; border: 2px dashed #cbd5e1;
                    border-radius: 12px; color: #94a3b8; font-size: 1rem;
                ">
                    Fill in bond details and click <strong>&nbsp;Calculate Price</strong>
                </div>
                """,
                unsafe_allow_html=True,
            )

# =====================================================================
#  TAB 2 — CURVE ANALYSIS
# =====================================================================
with tab2:
    col_curve_in, col_curve_sp, col_curve_out = st.columns([4, 0.5, 6])

    # ── Left column: Inputs ──
    with col_curve_in:
        st.markdown('<p class="section-title">Par Yield Inputs</p>', unsafe_allow_html=True)
        st.caption(
            "Enter current market par yields for standard maturities. "
            "The tool bootstraps zero-coupon spot rates and derives implied forward rates."
        )

        data = pd.DataFrame({
            "Maturity (Years)": [1, 2, 3, 5, 10, 30],
            "Par Yield (%)": [5.0, 5.5, 5.8, 6.2, 6.5, 6.8],
        })

        edited_data = st.data_editor(
            data,
            num_rows="dynamic",
            width='stretch',
            column_config={
                "Maturity (Years)": st.column_config.NumberColumn(format="%d"),
                "Par Yield (%)": st.column_config.NumberColumn(format="%.2f"),
            },
        )

        st.write("")
        analyze = st.button("Analyze Curve", use_container_width=True)

    # ── Right column: Results ──
    with col_curve_out:
        if analyze:
            try:
                df = edited_data.copy()
                df["Maturity (Years)"] = df["Maturity (Years)"].astype(int)
                df["Par Yield (%)"] = df["Par Yield (%)"].astype(float)
                par_yields = dict(zip(df["Maturity (Years)"], df["Par Yield (%)"]))

                if not par_yields:
                    st.warning("Please enter at least one maturity / yield pair.")
                else:
                    # Bootstrap spot curve
                    spot_curve = bootstrap_spot_curve(par_yields)

                    # Calculate forward rates for each adjacent pair
                    sorted_years = sorted(spot_curve.keys())
                    forwards = {}
                    for i in range(len(sorted_years) - 1):
                        t1, t2 = sorted_years[i], sorted_years[i + 1]
                        fwd = calculate_forward_rate(spot_curve[t1], t1, spot_curve[t2], t2)
                        forwards[f"{t1}Y \u2192 {t2}Y"] = fwd

                    st.markdown('<div class="results-banner">Analysis Results</div>', unsafe_allow_html=True)
                    st.write("")

                    # ── Side-by-side results tables ──
                    tbl1, tbl2 = st.columns(2)

                    with tbl1:
                        st.markdown('<p class="section-title">Bootstrapped Spot Rates</p>', unsafe_allow_html=True)
                        spot_df = pd.DataFrame(
                            list(spot_curve.items()),
                            columns=["Term (Y)", "Spot Rate (%)"],
                        )
                        spot_df["Spot Rate (%)"] = spot_df["Spot Rate (%)"].round(4)
                        st.dataframe(spot_df, width='stretch', hide_index=True)

                    with tbl2:
                        st.markdown('<p class="section-title">Implied Forward Rates</p>', unsafe_allow_html=True)
                        fwd_df = pd.DataFrame(
                            list(forwards.items()),
                            columns=["Period", "Forward Rate (%)"],
                        )
                        fwd_df["Forward Rate (%)"] = fwd_df["Forward Rate (%)"].round(4)
                        st.dataframe(fwd_df, width='stretch', hide_index=True)

                    # ── Combined chart ──
                    st.write("")
                    st.markdown('<p class="section-title">Rate Curves</p>', unsafe_allow_html=True)

                    chart_data = pd.DataFrame({
                        "Term": sorted_years,
                        "Par Yield": [par_yields.get(y, None) for y in sorted_years],
                        "Spot Rate": [spot_curve.get(y, None) for y in sorted_years],
                    })
                    chart_data = chart_data.set_index("Term")
                    st.line_chart(chart_data, width='stretch')

            except Exception as e:
                st.error(f"Analysis failed: {e}")
        else:
            st.markdown(
                """
                <div style="
                    display: flex; align-items: center; justify-content: center;
                    height: 340px; border: 2px dashed #cbd5e1;
                    border-radius: 12px; color: #94a3b8; font-size: 1rem;
                ">
                    Enter par yields and click <strong>&nbsp;Analyze Curve</strong>
                </div>
                """,
                unsafe_allow_html=True,
            )
