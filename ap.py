import streamlit as st
import streamlit.components.v1 as components
import math

st.set_page_config(page_title="Mine Fleet Calculator", page_icon="L2.png")

st.title("⛏️ Mining Fleet Capacity Calculator")
st.write("Quick diagnostic tool for engineers, supervisors, and shift foremen.")

# ---------------------------------------------------------
# INITIALISE SESSION STATE (All initial values set to 0)
# ---------------------------------------------------------
if "cycles" not in st.session_state:
    st.session_state.cycles = [
        {
            "cycle_time": 0.0,
            "excavators": [{"rate": 0.0}],
            "trucks": [{"capacity": 0.0, "count": 0}]
        }
    ]

# Track newly added cycle index for auto-scrolling
if "scroll_to_cycle" not in st.session_state:
    st.session_state.scroll_to_cycle = None

# ---------------------------------------------------------
# GLOBAL INPUTS (EQUIPMENT AVAILABILITY & STAFFING)
# ---------------------------------------------------------
st.header("Global Inputs & Availability")

daily_target = st.number_input("Daily Target (BCM)", value=0, min_value=0)

st.subheader("Excavator Fleet Metrics")
col_ex1, col_ex2 = st.columns(2)
ex_avail = col_ex1.number_input("Excavator Mechanical Availability (%)", value=0.0, min_value=0.0, max_value=100.0)
ex_util = col_ex2.number_input("Excavator Use of Availability (Utilisation %)", value=0.0, min_value=0.0, max_value=100.0)

st.subheader("Truck Fleet Metrics")
col_tr1, col_tr2 = st.columns(2)
tr_avail = col_tr1.number_input("Truck Mechanical Availability (%)", value=0.0, min_value=0.0, max_value=100.0)
tr_util = col_tr2.number_input("Truck Use of Availability (Utilisation %)", value=0.0, min_value=0.0, max_value=100.0)

st.subheader("Labor / Operator Constraints")
col_op1, col_op2 = st.columns(2)

# Count total configured units across all cycles for labor comparisons
total_ex_units = sum(len(c["excavators"]) for c in st.session_state.cycles)
total_tr_units = sum(sum(t["count"] for t in c["trucks"]) for c in st.session_state.cycles)

ex_operators = col_op1.number_input("Available Excavator Operators", value=0, min_value=0)
tr_operators = col_op2.number_input("Available Truck Operators", value=0, min_value=0)

# Effective equipment utilizations incorporating mechanical availability & UA
ex_effective_util = (ex_avail / 100.0) * (ex_util / 100.0)
tr_effective_util = (tr_avail / 100.0) * (tr_util / 100.0)

# Operator constraint scaling factor (caps fleet capacity if operators < physical units)
ex_labor_factor = min(1.0, ex_operators / total_ex_units) if total_ex_units > 0 else 1.0
tr_labor_factor = min(1.0, tr_operators / total_tr_units) if total_tr_units > 0 else 1.0

# ---------------------------------------------------------
# CYCLE TIMES (DIG BLOCK + DUMP LOCATION)
# ---------------------------------------------------------
st.header("Cycle Times (Dig Block + Dump Location)")

# Display each cycle time block
for c_idx, cycle in enumerate(st.session_state.cycles):

    # Anchor target for auto-scrolling to newly added cycle
    st.markdown(f'<div id="cycle_anchor_{c_idx}"></div>', unsafe_allow_html=True)

    st.subheader(f"Cycle Time Block {c_idx+1}")

    # Cycle time input
    cycle["cycle_time"] = st.number_input(
        f"Cycle Time {c_idx+1} (minutes)",
        value=float(cycle["cycle_time"]),
        min_value=0.0,
        key=f"cycle_time_{c_idx}"
    )

    # Remove cycle time button
    if st.button(f"➖ Remove Cycle Time {c_idx+1}", key=f"remove_cycle_{c_idx}"):
        st.session_state.cycles.pop(c_idx)
        st.session_state.scroll_to_cycle = None
        st.rerun()

    # ---------------------------------------------------------
    # EXCAVATORS UNDER THIS CYCLE
    # ---------------------------------------------------------
    st.write("### Excavators")

    if st.button("➕ Add Excavator", key=f"add_ex_{c_idx}"):
        cycle["excavators"].append({"rate": 0.0})
        st.rerun()

    for e_idx, ex in enumerate(cycle["excavators"]):
        cols = st.columns([3, 1])
        ex["rate"] = cols[0].number_input(
            f"Excavator {e_idx+1} Dig Rate (BCM/hr) — Cycle {c_idx+1}",
            value=float(ex["rate"]),
            min_value=0.0,
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
        cycle["trucks"].append({"capacity": 0.0, "count": 0})
        st.rerun()

    for t_idx, tr in enumerate(cycle["trucks"]):
        cols = st.columns([3, 3, 1])
        tr["capacity"] = cols[0].number_input(
            f"Truck Type {t_idx+1} Capacity (BCM) — Cycle {c_idx+1}",
            value=float(tr["capacity"]),
            min_value=0.0,
            key=f"tr_cap_{c_idx}_{t_idx}"
        )
        tr["count"] = cols[1].number_input(
            f"Truck Type {t_idx+1} Count — Cycle {c_idx+1}",
            value=int(tr["count"]),
            min_value=0,
            key=f"tr_count_{c_idx}_{t_idx}"
        )
        if cols[2].button("➖", key=f"remove_tr_{c_idx}_{t_idx}"):
            cycle["trucks"].pop(t_idx)
            st.rerun()

    # ➕ Add Cycle Time button placed at the bottom of the last cycle block
    if c_idx == len(st.session_state.cycles) - 1:
        st.write("---")
        if st.button("➕ Add Cycle Time", key="add_cycle_bottom"):
            st.session_state.cycles.append({
                "cycle_time": 0.0,
                "excavators": [{"rate": 0.0}],
                "trucks": [{"capacity": 0.0, "count": 0}]
            })
            st.session_state.scroll_to_cycle = len(st.session_state.cycles) - 1
            st.rerun()

# Auto-scroll trigger script for newly created cycle
if st.session_state.scroll_to_cycle is not None:
    target_idx = st.session_state.scroll_to_cycle
    components.html(
        f"""
        <script>
            window.parent.document.getElementById('cycle_anchor_{target_idx}')?.scrollIntoView({{behavior: 'smooth'}});
        </script>
        """,
        height=0,
    )
    st.session_state.scroll_to_cycle = None

# ---------------------------------------------------------
# CALCULATIONS PER CYCLE
# ---------------------------------------------------------
st.header("Cycle Production Results")

total_daily_dig = 0
total_daily_truck = 0
over_capacity_cycles = []
truck_bottleneck_cycles = []

for c_idx, cycle in enumerate(st.session_state.cycles):

    st.subheader(f"Cycle {c_idx+1} Results")

    cycle_time = cycle["cycle_time"]

    # Excavator production (adjusted by ex_avail, ex_util, and ex_labor_factor)
    dig_rate = sum(ex["rate"] for ex in cycle["excavators"])
    daily_dig = dig_rate * 24 * ex_effective_util * ex_labor_factor

    # Truck production (adjusted by tr_avail, tr_util, and tr_labor_factor)
    if cycle_time > 0:
        truck_hourly = sum(
            (60 / cycle_time) * tr["capacity"] * tr["count"] * tr_effective_util * tr_labor_factor
            for tr in cycle["trucks"]
        )
    else:
        truck_hourly = 0
        
    daily_truck = truck_hourly * 24

    total_daily_dig += daily_dig
    total_daily_truck += daily_truck

    st.write(f"**Dig Rate:** {dig_rate:,.0f} BCM/hr")
    st.write(f"**Daily Dig Capacity:** {daily_dig:,.0f} BCM/day")
    st.write(f"**Daily Truck Capacity:** {daily_truck:,.0f} BCM/day")

    # Estimate average capacity per truck to calculate required / excess truck units
    total_cycle_trucks = sum(tr["count"] for tr in cycle["trucks"])
    if total_cycle_trucks > 0 and daily_truck > 0:
        daily_bcm_per_truck = daily_truck / total_cycle_trucks
    else:
        avg_cap = (sum(tr["capacity"] for tr in cycle["trucks"]) / len(cycle["trucks"])) if cycle["trucks"] else 0
        daily_bcm_per_truck = ((60 / (cycle_time if cycle_time > 0 else 1)) * avg_cap * tr_effective_util * tr_labor_factor) * 24

    # Case A: Truck fleet cannot keep up with excavator dig rate
    if daily_truck < daily_dig and daily_dig > 0:
        shortfall_bcm = daily_dig - daily_truck
        needed_trucks = math.ceil(shortfall_bcm / daily_bcm_per_truck) if daily_bcm_per_truck > 0 else 0

        truck_bottleneck_cycles.append({
            "cycle_num": c_idx + 1,
            "shortfall_bcm": shortfall_bcm,
            "needed_trucks": needed_trucks
        })
        st.error(
            f"🚨 **Truck Bottleneck in Cycle {c_idx+1}:** "
            f"Truck capacity falls short of dig capacity by {shortfall_bcm:,.0f} BCM/day. "
            f"Needs ~**{needed_trucks} additional truck(s)** to match excavator output."
        )

    # Case B: Surplus truck capacity relative to excavator output
    elif daily_truck > daily_dig and daily_dig > 0:
        excess_bcm = daily_truck - daily_dig
        excess_trucks = excess_bcm / daily_bcm_per_truck if daily_bcm_per_truck > 0 else 0

        over_capacity_cycles.append({
            "cycle_num": c_idx + 1,
            "excess_bcm": excess_bcm,
            "excess_trucks": excess_trucks
        })
        st.warning(
            f"ℹ️ **Truck Over-Capacity in Cycle {c_idx+1}:** "
            f"Truck haul capacity exceeds dig capacity by {excess_bcm:,.0f} BCM/day "
            f"(~{excess_trucks:.1f} excess trucks)."
        )

# ---------------------------------------------------------
# OVERALL VERDICT
# ---------------------------------------------------------
st.header("Overall Fleet Verdict")

st.write(f"**Total Daily Dig Capacity:** {total_daily_dig:,.0f} BCM/day")
st.write(f"**Total Daily Truck Capacity:** {total_daily_truck:,.0f} BCM/day")

# Operator warnings
if ex_labor_factor < 1.0:
    st.warning(f"⚠️ Dig capacity is restricted by labor: {ex_operators} operators for {total_ex_units} excavators.")
if tr_labor_factor < 1.0:
    st.warning(f"⚠️ Truck capacity is restricted by labor: {tr_operators} operators for {total_tr_units} trucks.")

# Overall capacity verdict
if daily_target == 0:
    st.info("💡 Set a Daily Target (BCM) greater than 0 to evaluate overall fleet capacity.")
elif total_daily_truck < daily_target:
    st.error("❌ Fleet cannot meet daily target. Truck capacity is the bottleneck.")
    if truck_bottleneck_cycles:
        st.markdown("### 🚜 Resource Allocation Required:")
        for item in truck_bottleneck_cycles:
            st.write(
                f"- **Cycle {item['cycle_num']}:** Deficit of **{item['shortfall_bcm']:,.0f} BCM/day**. "
                f"Add at least **{item['needed_trucks']} truck(s)** to clear this cycle's bottleneck."
            )
elif total_daily_dig < daily_target:
    st.error("❌ Fleet cannot meet daily target. Dig rate (excavators) is the bottleneck.")
else:
    st.success("✅ Fleet can meet daily target.")
    if over_capacity_cycles:
        st.info("🚜 **Over-Capacity Analysis:** Target is achieved, but you have excess truck capacity in:")
        for item in over_capacity_cycles:
            st.write(
                f"- **Cycle {item['cycle_num']}:** Surplus of **{item['excess_bcm']:,.0f} BCM/day** "
                f"(approx. **{item['excess_trucks']:.1f}** idle/redundant trucks relative to dig output)."
            )
    else:
        st.info("👌 **Balanced Fleet:** Truck capacity closely matches dig capacity across all cycles.")
