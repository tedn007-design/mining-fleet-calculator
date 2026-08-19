import streamlit as st
import math

st.set_page_config(page_title="Mine Fleet Calculator", page_icon=None)

st.title("Mining Fleet Capacity Calculator")
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

# ---------------------------------------------------------
# GLOBAL INPUTS (EQUIPMENT AVAILABILITY & STAFFING)
# ---------------------------------------------------------
st.header("Global Inputs & Availability")

daily_target = st.number_input("Daily Target (BCM)", value=0, min_value=0, key="daily_target")

st.subheader("Excavator Fleet Metrics")
col_ex1, col_ex2 = st.columns(2)
ex_avail = col_ex1.number_input("Excavator Mechanical Availability (%)", value=0.0, min_value=0.0, max_value=100.0, key="ex_avail")
ex_util = col_ex2.number_input("Excavator Use of Availability (Utilisation %)", value=0.0, min_value=0.0, max_value=100.0, key="ex_util")

st.subheader("Truck Fleet Metrics")
col_tr1, col_tr2 = st.columns(2)
tr_avail = col_tr1.number_input("Truck Mechanical Availability (%)", value=0.0, min_value=0.0, max_value=100.0, key="tr_avail")
tr_util = col_tr2.number_input("Truck Use of Availability (Utilisation %)", value=0.0, min_value=0.0, max_value=100.0, key="tr_util")

st.subheader("Labor / Operator Constraints")
col_op1, col_op2 = st.columns(2)

total_ex_units = sum(len(c["excavators"]) for c in st.session_state.cycles)
total_tr_units = sum(sum(t["count"] for t in c["trucks"]) for c in st.session_state.cycles)

ex_operators = col_op1.number_input("Available Excavator Operators", value=0, min_value=0, key="ex_operators")
tr_operators = col_op2.number_input("Available Truck Operators", value=0, min_value=0, key="tr_operators")

ex_effective_util = (ex_avail / 100.0) * (ex_util / 100.0)
tr_effective_util = (tr_avail / 100.0) * (tr_util / 100.0)

ex_labor_factor = min(1.0, ex_operators / total_ex_units) if total_ex_units > 0 else 1.0
tr_labor_factor = min(1.0, tr_operators / total_tr_units) if total_tr_units > 0 else 1.0

# ---------------------------------------------------------
# CYCLE TIMES (DIG BLOCK + DUMP LOCATION)
# ---------------------------------------------------------
st.header("Cycle Times (Dig Block + Dump Location)")

for c_idx, cycle in enumerate(st.session_state.cycles):
    st.subheader(f"Cycle Time Block {c_idx+1}")

    cycle["cycle_time"] = st.number_input(
        f"Cycle Time {c_idx+1} (minutes)",
        value=float(cycle["cycle_time"]),
        min_value=0.0,
        key=f"cycle_time_{c_idx}"
    )

    if st.button(f"Remove Cycle Time {c_idx+1}", key=f"remove_cycle_{c_idx}"):
        st.session_state.cycles.pop(c_idx)
        st.rerun()

    st.write("### Excavators")
    if st.button("Add Excavator", key=f"add_ex_{c_idx}"):
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
        if cols[1].button("Remove", key=f"remove_ex_{c_idx}_{e_idx}"):
            cycle["excavators"].pop(e_idx)
            st.rerun()

    st.write("### Trucks")
    if st.button("Add Truck Type", key=f"add_tr_{c_idx}"):
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
        if cols[2].button("Remove", key=f"remove_tr_{c_idx}_{t_idx}"):
            cycle["trucks"].pop(t_idx)
            st.rerun()

    if c_idx == len(st.session_state.cycles) - 1:
        st.write("---")
        if st.button("Add Cycle Time", key="add_cycle_bottom"):
            st.session_state.cycles.append({
                "cycle_time": 0.0,
                "excavators": [{"rate": 0.0}],
                "trucks": [{"capacity": 0.0, "count": 0}]
            })
            st.rerun()

# ---------------------------------------------------------
# CALCULATIONS PER CYCLE
# ---------------------------------------------------------
st.header("Cycle Production Results")

total_daily_dig = 0
total_daily_truck = 0
over_capacity_cycles = []
truck_bottleneck_cycles = []
cycle_summary = []

for c_idx, cycle in enumerate(st.session_state.cycles):
    st.subheader(f"Cycle {c_idx+1} Results")
    cycle_time = cycle["cycle_time"]

    dig_rate = sum(ex["rate"] for ex in cycle["excavators"])
    daily_dig = dig_rate * 24 * ex_effective_util * ex_labor_factor

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

    total_cycle_trucks = sum(tr["count"] for tr in cycle["trucks"])
    if total_cycle_trucks > 0 and daily_truck > 0:
        daily_bcm_per_truck = daily_truck / total_cycle_trucks
    else:
        avg_cap = (sum(tr["capacity"] for tr in cycle["trucks"]) / len(cycle["trucks"])) if cycle["trucks"] else 0
        daily_bcm_per_truck = ((60 / (cycle_time if cycle_time > 0 else 1)) * avg_cap * tr_effective_util * tr_labor_factor) * 24

    c_info = {
        "cycle_num": c_idx + 1,
        "cycle_time": cycle_time,
        "dig_rate": dig_rate,
        "daily_dig": daily_dig,
        "daily_truck": daily_truck,
        "total_trucks": total_cycle_trucks,
        "daily_bcm_per_truck": daily_bcm_per_truck,
        "trucks": cycle["trucks"]
    }
    cycle_summary.append(c_info)

    if daily_truck < daily_dig and daily_dig > 0:
        shortfall_bcm = daily_dig - daily_truck
        needed_trucks = math.ceil(shortfall_bcm / daily_bcm_per_truck) if daily_bcm_per_truck > 0 else 0
        c_info["shortfall_bcm"] = shortfall_bcm
        c_info["needed_trucks"] = needed_trucks
        truck_bottleneck_cycles.append(c_info)

        st.error(
            f"**Truck Shortage on Cycle {c_idx+1}:** "
            f"Trucks fall short of dig capacity by {shortfall_bcm:,.0f} BCM/day. "
            f"Needs ~**{needed_trucks} more truck(s)**."
        )

    elif daily_truck > daily_dig and daily_dig > 0:
        excess_bcm = daily_truck - daily_dig
        excess_trucks = math.floor(excess_bcm / daily_bcm_per_truck) if daily_bcm_per_truck > 0 else 0
        c_info["excess_bcm"] = excess_bcm
        c_info["excess_trucks"] = excess_trucks
        over_capacity_cycles.append(c_info)

        st.warning(
            f"**Extra Truck Capacity on Cycle {c_idx+1}:** "
            f"Truck capacity exceeds dig output by {excess_bcm:,.0f} BCM/day "
            f"(~{excess_trucks} redundant truck(s) queuing/waiting)."
        )

# ---------------------------------------------------------
# OPTIMIZATION HELPER
# ---------------------------------------------------------
def evaluate_reallocation_scenarios(cycles, daily_target, tr_effective_util, tr_labor_factor, ex_effective_util, ex_labor_factor):
    all_trucks = []
    for c_idx, c in enumerate(cycles):
        for tr in c["trucks"]:
            for _ in range(tr["count"]):
                if tr["capacity"] > 0:
                    all_trucks.append({"capacity": tr["capacity"], "orig_cycle": c_idx})
    
    if not all_trucks or len(cycles) < 2:
        return None

    def calculate_total_system_output(assignment):
        total_output = 0
        cycle_outputs = []
        for c_idx, c in enumerate(cycles):
            cycle_time = c["cycle_time"]
            daily_dig = sum(ex["rate"] for ex in c["excavators"]) * 24 * ex_effective_util * ex_labor_factor
            assigned_trucks = assignment[c_idx]
            
            daily_truck = sum((60 / cycle_time) * cap * tr_effective_util * tr_labor_factor for cap in assigned_trucks) * 24 if cycle_time > 0 else 0
            effective_cycle_output = min(daily_dig, daily_truck)
            total_output += effective_cycle_output
            cycle_outputs.append({
                "daily_dig": daily_dig,
                "daily_truck": daily_truck,
                "effective": effective_cycle_output,
                "trucks": assigned_trucks
            })
        return total_output, cycle_outputs

    best_assignment = None
    best_output = 0
    num_cycles = len(cycles)
    
    def partition_trucks(truck_index, current_assignment):
        nonlocal best_assignment, best_output
        if truck_index == len(all_trucks):
            out, _ = calculate_total_system_output(current_assignment)
            if out > best_output:
                best_output = out
                best_assignment = [list(c) for c in current_assignment]
            return

        for c_i in range(num_cycles):
            current_assignment[c_i].append(all_trucks[truck_index]["capacity"])
            partition_trucks(truck_index + 1, current_assignment)
            current_assignment[c_i].pop()

    partition_trucks(0, [[] for _ in range(num_cycles)])

    if best_assignment:
        total_out, c_details = calculate_total_system_output(best_assignment)
        return {
            "best_output": total_out,
            "gap": max(0, daily_target - total_out) if daily_target > 0 else 0,
            "cycle_details": c_details
        }
    return None

# ---------------------------------------------------------
# OVERALL VERDICT & REALLOCATION RECOMMENDATIONS
# ---------------------------------------------------------
st.header("Overall Fleet Verdict")

effective_fleet_capacity = min(total_daily_dig, total_daily_truck)

st.write(f"**Total Daily Dig Capacity:** {total_daily_dig:,.0f} BCM/day")
st.write(f"**Total Daily Truck Capacity:** {total_daily_truck:,.0f} BCM/day")
st.write(f"**Actual Deliverable Fleet Output:** {effective_fleet_capacity:,.0f} BCM/day")

if ex_labor_factor < 1.0:
    st.warning(f"Digger output limited by operator shortage: {ex_operators} operators for {total_ex_units} excavators.")
if tr_labor_factor < 1.0:
    st.warning(f"Truck output limited by operator shortage: {tr_operators} operators for {total_tr_units} trucks.")

st.markdown("---")

if daily_target == 0:
    st.info("Set a Daily Target (BCM) above 0 to see target checks.")

elif effective_fleet_capacity >= daily_target:
    st.success(f"**Fleet CAN meet daily target!** (Delivers {effective_fleet_capacity:,.0f} BCM/day vs target of {daily_target:,.0f} BCM/day)")
    
    st.subheader("Target Over-Capacity & Ancillary Deployment Opportunities")
    
    excess_capacity_bcm = effective_fleet_capacity - daily_target
    
    avg_truck_bcm_day = (total_daily_truck / total_tr_units) if total_tr_units > 0 else 1
    redundant_trucks = math.floor(excess_capacity_bcm / avg_truck_bcm_day) if avg_truck_bcm_day > 0 else 0

    if redundant_trucks > 0:
        st.info(
            f"**Target Exceeded by {excess_capacity_bcm:,.0f} BCM/day:**\n\n"
            f"- Your fleet is producing more than required by your {daily_target:,.0f} BCM plan.\n"
            f"- You have **~{redundant_trucks} truck(s)** above what is needed to hit target.\n"
            f"- **Recommendation:** Pull **{redundant_trucks} truck(s)** off main production and deploy them to ancillary tasks "
            f"(e.g., **Topsoil stripping, ROM Rehandle, Road maintenance, or Civil works**)."
        )
    else:
        st.info(
            f"Fleet output matches your plan closely. All trucks are required on current circuits to safely hit the {daily_target:,.0f} BCM target."
        )

    if over_capacity_cycles:
        st.write("**Local Digger Queuing Check:**")
        for item in over_capacity_cycles:
            st.caption(f"- Cycle {item['cycle_num']}: Digger has {item['excess_bcm']:,.0f} BCM/day extra truck capacity queuing in the pit.")

else:
    st.error(f"**Fleet CANNOT meet daily target.** Current fleet delivers {effective_fleet_capacity:,.0f} BCM/day vs target of {daily_target:,.0f} BCM/day (Shortfall: {daily_target - effective_fleet_capacity:,.0f} BCM/day).")

    st.subheader("Shift Action Options to Fix the Bottleneck")
    
    st.markdown("#### Option 1: Move Existing Trucks Between Diggers")
    if len(st.session_state.cycles) > 1:
        opt_result = evaluate_reallocation_scenarios(
            st.session_state.cycles, daily_target, tr_effective_util, tr_labor_factor, ex_effective_util, ex_labor_factor
        )

        if opt_result:
            new_output = opt_result["best_output"]
            improvement = new_output - effective_fleet_capacity

            if improvement > 50:
                st.success(f"Moving trucks increases site output by **+{improvement:,.0f} BCM/day** to **{new_output:,.0f} BCM/day**!")
                st.write("**Recommended Shift Directives:**")
                for c_idx, det in enumerate(opt_result["cycle_details"]):
                    orig_count = sum(tr["count"] for tr in st.session_state.cycles[c_idx]["trucks"])
                    new_count = len(det["trucks"])
                    diff = new_count - orig_count
                    
                    cap_counts = {}
                    for cap in det["trucks"]:
                        cap_counts[cap] = cap_counts.get(cap, 0) + 1
                    tr_str = ", ".join([f"{count}x {cap:g} BCM truck(s)" for cap, count in cap_counts.items()]) if cap_counts else "no trucks"

                    if diff < 0:
                        st.write(f"- **Took {abs(diff)} truck(s) away from Cycle {c_idx+1}** (leaves {new_count} truck(s): {tr_str}).")
                    elif diff > 0:
                        st.write(f"- **Added {diff} truck(s) to Cycle {c_idx+1}** (gives {new_count} truck(s): {tr_str}).")
                    else:
                        st.write(f"- **Kept Cycle {c_idx+1} at {new_count} truck(s)** ({tr_str}).")
            else:
                st.write("**Trucks are already placed on their best circuits.** Swapping existing trucks around will not produce extra dirt.")
    else:
        st.write("*(Add more cycle blocks to compare truck movements)*")

    st.markdown("#### Option 2: Shave Time Off Haul Cycles")
    for item in cycle_summary:
        if item["daily_truck"] > 0 and item["cycle_time"] > 0 and item["daily_truck"] < item["daily_dig"]:
            target_cycle_time = item["cycle_time"] * (item["daily_truck"] / item["daily_dig"])
            time_reduction = item["cycle_time"] - target_cycle_time
            st.write(f"- **Cycle {item['cycle_num']}:** Cut round-trip time from **{item['cycle_time']:.1f} mins** to **{target_cycle_time:.1f} mins** (shave off **{time_reduction:.1f} mins** per lap).")

    st.markdown("#### Option 3: Bring in Additional Trucks from Park-Up")
    for item in truck_bottleneck_cycles:
        if item["daily_bcm_per_truck"] > 0:
            add_trucks = math.ceil(item["shortfall_bcm"] / item["daily_bcm_per_truck"])
            st.write(f"- **Cycle {item['cycle_num']}:** Needs **{add_trucks} extra truck(s)** to keep up with the digger (recovers **{item['shortfall_bcm']:,.0f} BCM/day**).")
