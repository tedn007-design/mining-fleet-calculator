import streamlit as st

st.set_page_config(page_title="Mining Fleet Capacity Calculator", page_icon="⛏️")

st.title("⛏️ Mining Fleet Capacity Calculator")
st.write("Quick diagnostic tool for engineers, supervisors, and shift foremen.")

# -----------------------------
# INPUT PARAMETERS
# -----------------------------
st.header("Input Parameters")

daily_target = st.number_input("Daily Target (BCM)", value=40000)

st.subheader("Excavator Dig Rates (BCM/hr)")
ex1 = st.number_input("Excavator 1 Dig Rate", value=950)
ex2 = st.number_input("Excavator 2 Dig Rate", value=900)
ex3 = st.number_input("Excavator 3 Dig Rate", value=450)

st.subheader("Truck Fleet")
num_trucks = st.number_input("Number of Trucks", value=15)
truck_capacity = st.number_input("Truck Capacity (BCM)", value=105)

st.subheader("Cycle Time")
cycle_time_min = st.number_input("Actual Cycle Time (minutes)", value=42)

st.subheader("Availability & Utilisation")
availability = st.number_input("Mechanical Availability (%)", value=90)
utilisation = st.number_input("Use of Availability (Utilisation %)", value=85)

# Effective Utilisation = Availability × Utilisation
effective_utilisation = (availability / 100) * (utilisation / 100)

# -----------------------------
# CALCULATIONS
# -----------------------------
total_dig_rate = ex1 + ex2 + ex3
daily_dig_capacity = total_dig_rate * 24 * effective_utilisation

truck_hourly_capacity = (60 / cycle_time_min) * truck_capacity * num_trucks * effective_utilisation
daily_truck_capacity = truck_hourly_capacity * 24

# -----------------------------
# ALERTS SECTION
# -----------------------------
st.header("Operational Alerts")

# Cycle time alerts
if cycle_time_min > 45:
    st.error("❌ Cycle time is critically high. Immediate investigation required.")
elif cycle_time_min > 40:
    st.warning("⚠️ Cycle time above optimal range. Check delays or haul road conditions.")
else:
    st.success("✅ Cycle time within optimal range.")

# Dig rate alerts
if ex1 < 800 or ex2 < 800 or ex3 < 400:
    st.error("❌ One or more excavators are digging below expected performance.")
elif ex1 < 900 or ex2 < 900 or ex3 < 450:
    st.warning("⚠️ Excavator dig rates slightly below target. Monitor performance.")
else:
    st.success("✅ Excavator dig rates are healthy.")

# Availability alerts
if availability < 80:
    st.error("❌ Mechanical Availability critically low. Major breakdown or maintenance delays.")
elif availability < 90:
    st.warning("⚠️ Availability slightly below target. Review maintenance planning.")
else:
    st.success("✅ Availability within expected range.")

# Utilisation alerts (Use of Availability)
if utilisation < 70:
    st.error("❌ Utilisation critically low. Excessive idle time or operational delays.")
elif utilisation < 85:
    st.warning("⚠️ Utilisation slightly below target. Check dispatch efficiency.")
else:
    st.success("✅ Utilisation healthy.")

# Effective Utilisation alerts
if effective_utilisation < 0.60:
    st.error("❌ Effective Utilisation (Avail × Util) critically low. Fleet output severely impacted.")
elif effective_utilisation < 0.75:
    st.warning("⚠️ Effective Utilisation below optimal. Review shift performance.")
else:
    st.success("✅ Effective Utilisation strong.")

# -----------------------------
# PRODUCTION VERDICT
# -----------------------------
st.header("Production Verdict")

st.write(f"**Total Dig Rate:** {total_dig_rate} BCM/hr")
st.write(f"**Daily Dig Capacity (adjusted):** {daily_dig_capacity:,.0f} BCM/day")
st.write(f"**Daily Truck Capacity (adjusted):** {daily_truck_capacity:,.0f} BCM/day")
st.write(f"**Effective Utilisation (Avail × Util):** {effective_utilisation:.2f}")

if daily_truck_capacity < daily_target:
    st.error("❌ Fleet cannot meet daily target. Truck capacity is the bottleneck.")
elif daily_dig_capacity < daily_target:
    st.error("❌ Fleet cannot meet daily target. Dig rate is the bottleneck.")
else:
    st.success("✅ Fleet can meet daily target.")

# -----------------------------
# SUMMARY
# -----------------------------
st.header("Summary")
st.write("""
- Corrected terminology: Utilisation = Use of Availability  
- Effective Utilisation (Avail × Util) now drives all production calculations  
- Alerts highlight cycle time, dig rate, availability, utilisation, and effective utilisation  
- Use this tool during pre‑start, mid‑shift checks, and production troubleshooting  
""")
