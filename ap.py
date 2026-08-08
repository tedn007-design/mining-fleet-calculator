import streamlit as st

st.set_page_config(page_title="Mining Fleet Capacity Calculator", layout="wide")

st.title("⛏️ Mining Fleet Capacity Calculator")
st.write("Quick diagnostic tool for engineers, supervisors, and shift foremen.")

# --- INPUTS ---
st.header("Input Parameters")

daily_target = st.number_input("Daily Target (BCM)", value=40000)
ex1 = st.number_input("Excavator 1 Dig Rate (BCM/hr)", value=950)
ex2 = st.number_input("Excavator 2 Dig Rate (BCM/hr)", value=850)
ex3 = st.number_input("Excavator 3 Dig Rate (BCM/hr)", value=450)

truck_capacity = st.number_input("Truck Capacity (BCM)", value=108)
cycle_time_min = st.number_input("Truck Cycle Time (minutes)", value=42)
num_trucks = st.number_input("Number of Trucks", value=15)
utilisation = st.slider("Utilisation (%)", 50, 100, 85)

# --- CALCULATIONS ---
hourly_target = daily_target / 24
total_dig_rate = ex1 + ex2 + ex3
cycle_time_hr = cycle_time_min / 60
truck_prod = truck_capacity / cycle_time_hr
fleet_capacity = truck_prod * num_trucks

excavator_effective = total_dig_rate * (utilisation / 100)
truck_effective = fleet_capacity * (utilisation / 100)

# --- OUTPUT ---
st.header("Results")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Excavator Capacity")
    st.write(f"Hourly Target: **{hourly_target:.1f} BCM/hr**")
    st.write(f"Total Dig Rate: **{total_dig_rate:.1f} BCM/hr**")
    st.write(f"Effective Dig Rate (@{utilisation}%): **{excavator_effective:.1f} BCM/hr**")

with col2:
    st.subheader("Truck Fleet Capacity")
    st.write(f"Truck Productivity: **{truck_prod:.1f} BCM/hr per truck**")
    st.write(f"Fleet Capacity: **{fleet_capacity:.1f} BCM/hr**")
    st.write(f"Effective Fleet Capacity (@{utilisation}%): **{truck_effective:.1f} BCM/hr**")

# --- VERDICT ---
st.header("Verdict")

if excavator_effective >= hourly_target and truck_effective >= hourly_target:
    st.success("✅ Target Achievable — Fleet capacity exceeds hourly requirement.")
else:
    st.error("❌ Target NOT Achievable — Bottleneck detected.")

# --- BOTTLENECK IDENTIFICATION ---
st.header("Bottleneck Analysis")

if excavator_effective < hourly_target:
    st.warning("⚠️ Excavators are the bottleneck.")
elif truck_effective < hourly_target:
    st.warning("⚠️ Truck fleet is the bottleneck.")
else:
    st.info("No bottlenecks detected.")

# --- MINIMUM TRUCKS REQUIRED ---
min_trucks_required = hourly_target / truck_prod

st.header("Minimum Trucks Required")
st.write(f"To hit the target, you need at least **{min_trucks_required:.1f} trucks** at 100% utilisation.")
