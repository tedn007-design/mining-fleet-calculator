import streamlit as st

st.set_page_config(page_title="Mine Fleet Calculator", page_icon="L2.png")

st.title("⛏️ Mining Fleet Capacity Calculator")
st.write("Quick diagnostic tool for engineers, supervisors, and shift foremen.")

# ---------------------------------------------------------
# INITIALISE SESSION STATE LISTS
# ---------------------------------------------------------
if "excavators" not in st.session_state:
    st.session_state.excavators = [{"rate": 950}]
if "trucks" not in st.session_state:
    st.session_state.trucks = [{"capacity": 105, "count": 15}]

# ---------------------------------------------------------
# INPUT PARAMETERS
# ---------------------------------------------------------
st.header("Input Parameters")

daily_target = st.number_input("Daily Target (BCM)", value=40000)

# ---------------------------------------------------------
# DYNAMIC EXCAVATORS
# ---------------------------------------------------------
st.subheader("Excavators (Add or Remove)")

# Add new excavator
if st.button("➕ Add Excavator"):
    st.session_state.excavators.append({"rate": 0})

# Display excavators with remove buttons
for i, ex in enumerate(st.session_state.excavators):
    cols = st.columns([3, 1])
    st.session_state.excavators[i]["rate"] = cols[0].number_input(
        f"Excavator {i+1} Dig Rate (BCM/hr)",
        value=ex["rate"],
        key=f"ex_{i}"
    )

    # Remove button (minus sign)
    if cols[1].button("➖", key=f"remove_ex_{i}"):
        st.session_state.excavators.pop(i)
        st.rerun()

# ---------------------------------------------------------
# DYNAMIC TRUCK TYPES
# ---------------------------------------------------------
st.subheader("Truck Fleet (Add or Remove Truck Types)")

# Add new truck type
if st.button("➕ Add Truck Type"):
    st.session_state.trucks.append({"capacity": 0, "count": 0})

# Display truck types with remove buttons
for i, tr in enumerate(st.session_state.trucks):
    cols = st.columns([3, 3, 1])

    st.session_state.trucks[i]["capacity"] = cols[0].number_input(
        f"Truck Type {i+1} Capacity (BCM)",
        value=tr["capacity"],
        key=f"tr_cap_{i}"
    )

    st.session_state.trucks[i]["count"] = cols[1].number_input(
        f"Truck Type {i+1} Count",
        value=tr["count"],
        key=f"tr_count_{i}"
    )

    # Remove button (minus sign)
    if cols[2].button("➖", key=f"remove_tr_{i}"):
        st.session_state.trucks.pop(i)
        st.rerun()

# ---------------------------------------------------------
# CYCLE TIME & UTILISATION
# ---------------------------------------------------------
st.subheader("Cycle Time")
cycle_time_min = st.number_input("Actual Cycle Time (minutes)", value=42)

st.subheader("Availability & Utilisation")
availability = st.number_input("Mechanical Availability (%)", value=90)
utilisation = st.number_input("Use of Availability (Utilisation %)", value=85)

effective_utilisation = (availability / 100) * (utilisation / 100)

# ---------------------------------------------------------
# CALCULATIONS
# ---------------------------------------------------------
total_dig_rate = sum(ex["rate"] for ex in st.session_state.excavators)
daily_dig_capacity = total_dig_rate * 24 * effective_utilisation

truck_hourly_capacity = sum(
    (60 / cycle_time_min) * tr["capacity"] * tr["count"] * effective_utilisation
    for tr in st.session_state.trucks
)
daily_truck_capacity = truck_hourly_capacity * 24

# ---------------------------------------------------------
# ALERTS
# ---------------------------------------------------------
st.header("Operational Alerts")

# Cycle time alerts
if cycle_time_min > 45:
    st.error("❌ Cycle time is critically high. Immediate investigation required.")
elif cycle_time_min > 40:
    st.warning("⚠️ Cycle time above optimal range. Check delays or haul road conditions.")
else:
    st.success("✅ Cycle time within optimal range.")

# Dig rate alerts
if any(ex["rate"] < 400 for ex in st.session_state.excavators):
    st.error("❌ One or more excavators are digging below expected performance.")
elif any(ex["rate"] < 900 for ex in st.session_state.excavators):
    st.warning("⚠️ Excavator dig rates slightly below target. Monitor performance.")
else:
    st.success("✅ Excavator dig rates are healthy.")

# Availability alerts
if availability < 80:
    st.error("❌ Mechanical Availability critically low.")
elif availability < 90:
    st.warning("⚠️ Availability slightly below target.")
else:
    st.success("✅ Availability within expected range.")

# Utilisation alerts
if utilisation < 70:
    st.error("❌ Utilisation critically low.")
elif utilisation < 85:
    st.warning("⚠️ Utilisation slightly below target.")
else:
    st.success("✅ Utilisation healthy.")

# Effective utilisation alerts
if effective_utilisation < 0.60:
    st.error("❌ Effective Utilisation critically low.")
elif effective_utilisation < 0.75:
    st.warning("⚠️ Effective Utilisation below optimal.")
else:
    st.success("✅ Effective Utilisation strong.")

# ---------------------------------------------------------
# PRODUCTION VERDICT
# ---------------------------------------------------------
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
