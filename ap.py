import streamlit as st

st.set_page_config(page_title="Mine Fleet Calculator", page_icon="L2.png")

st.title("⛏️ Mining Fleet Capacity Calculator")
st.write("Quick diagnostic tool for engineers, supervisors, and shift foremen.")

# ---------------------------------------------------------
# INITIALISE SESSION STATE
# ---------------------------------------------------------
if "cycles" not in st.session_state:
    st.session_state.cycles = [
        {
            "cycle_time": 42,
            "excavators": [{"rate": 950}],
            "trucks": [{"capacity": 105, "count": 15}]
        }
    ]

# ---------------------------------------------------------
# ADD / REMOVE CYCLE TIMES
# ---------------------------------------------------------
st.header("Cycle Times (Dig Block + Dump Location)")

if st.button("➕ Add Cycle Time"):
    st.session_state.cycles.append({
        "cycle_time": 0,
        "excavators": [{"rate": 0}],
        "trucks": [{"capacity": 0, "count": 0}]
    })

# Display each cycle time block
for c_idx, cycle in enumerate(st.session_state.cycles):

    st.subheader(f"Cycle Time Block {c_idx+1}")

    # Cycle time input
    cycle["cycle_time"] = st.number_input(
        f"Cycle Time {c_idx+1} (minutes)",
        value=cycle["cycle_time"],
        key=f"cycle_time_{c_idx}"
    )

    # Remove cycle time
    if st.button(f"➖ Remove Cycle Time {c_idx+1}", key=f"remove_cycle_{c_idx}"):
        st.session_state.cycles.pop(c_idx)
        st.rerun()

    # ---------------------------------------------------------
    # EXCAVATORS UNDER THIS CYCLE
    # ---------------------------------------------------------
    st.write("### Excavators")

    if st.button("➕ Add Excavator", key=f"add_ex_{c_idx}"):
        cycle["excavators"].append({"rate": 0})

    for e_idx, ex in enumerate(cycle["excavators"]):
        cols = st.columns([3, 1])
        ex["rate"] = cols[0].number_input(
            f"Excavator {e_idx+1} Dig Rate (BCM/hr) — Cycle {c_idx+1}",
            value=ex["rate"],
            key=f"ex_{c_idx}_{e_idx}"
        )
        if cols[1].button("➖", key=f"remove_ex_{c_idx}_{e_idx}"):
            cycle["excavators"].pop(e_idx)
            st.rerun()

    # ---------------------------------------------------------
    # TRUCKS UNDER THIS CYCLE
    # ---------------------------------------------------------
    st.write("### Trucks")

    if st.button("➕ Add Truck Type", key=f"add_tr_{c_idx}"):
        cycle["trucks"].append({"capacity": 0, "count": 0})

    for t_idx, tr in enumerate(cycle["trucks"]):
        cols = st.columns([3, 3, 1])
        tr["capacity"] = cols[0].number_input(
            f"Truck Type {t_idx+1} Capacity (BCM) — Cycle {c_idx+1}",
            value=tr["capacity"],
            key=f"tr_cap_{c_idx}_{t_idx}"
        )
        tr["count"] = cols[1].number_input(
            f"Truck Type {t_idx+1} Count — Cycle {c_idx+1}",
            value=tr["count"],
            key=f"tr_count_{c_idx}_{t_idx}"
        )
        if cols[2].button("➖", key=f"remove_tr_{c_idx}_{t_idx}"):
            cycle["trucks"].pop(t_idx)
            st.rerun()

# ---------------------------------------------------------
# GLOBAL INPUTS
# ---------------------------------------------------------
st.header("Global Inputs")

daily_target = st.number_input("Daily Target (BCM)", value=40000)
availability = st.number_input("Mechanical Availability (%)", value=90)
utilisation = st.number_input("Use of Availability (Utilisation %)", value=85)

effective_utilisation = (availability / 100) * (utilisation / 100)

# ---------------------------------------------------------
# CALCULATIONS PER CYCLE
# ---------------------------------------------------------
st.header("Cycle Production Results")

total_daily_dig = 0
total_daily_truck = 0

for c_idx, cycle in enumerate(st.session_state.cycles):

    st.subheader(f"Cycle {c_idx+1} Results")

    cycle_time = cycle["cycle_time"]

    dig_rate = sum(ex["rate"] for ex in cycle["excavators"])
    daily_dig = dig_rate * 24 * effective_utilisation

    truck_hourly = sum(
        (60 / cycle_time) * tr["capacity"] * tr["count"] * effective_utilisation
        for tr in cycle["trucks"]
    )
    daily_truck = truck_hourly * 24

    total_daily_dig += daily_dig
    total_daily_truck += daily_truck

    st.write(f"**Dig Rate:** {dig_rate} BCM/hr")
    st.write(f"**Daily Dig Capacity:** {daily_dig:,.0f} BCM/day")
    st.write(f"**Daily Truck Capacity:** {daily_truck:,.0f} BCM/day")

# ---------------------------------------------------------
# OVERALL VERDICT
# ---------------------------------------------------------
st.header("Overall Fleet Verdict")

st.write(f"**Total Daily Dig Capacity:** {total_daily_dig:,.0f} BCM/day")
st.write(f"**Total Daily Truck Capacity:** {total_daily_truck:,.0f} BCM/day")

if total_daily_truck < daily_target:
    st.error("❌ Fleet cannot meet daily target. Truck capacity is the bottleneck.")
elif total_daily_dig < daily_target:
    st.error("❌ Fleet cannot meet daily target. Dig rate is the bottleneck.")
else:
    st.success("✅ Fleet can meet daily target.")
