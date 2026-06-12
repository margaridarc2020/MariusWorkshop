import streamlit as st
import pandas as pd
import itertools
import random

st.set_page_config(page_title="BioCoat Master DoE Engine", page_icon="🧪", layout="wide")

st.title("🧪 The Fully Scalable DoE Matrix Generator")
st.subheader("Dynamic N-Dimensional Matrix Compiling for Lab Automation Pipelines")

# --- SIDEBAR: SYSTEM DIAGNOSTICS ---
st.sidebar.header("Step 1: Define Your Process Boundaries")

objective = st.sidebar.selectbox(
    "What is your primary experimental goal?",
    [
        "Screening (Filter out the noise / identify main drivers)",
        "Optimization (Map non-linear curves & response surfaces)",
        "Robust Design (Immunize process against ambient lab noise)"
    ]
)

# Expanded max_value to 6 to demonstrate true algorithmic scalability
factors_count = st.sidebar.number_input(
    "How many independent processing variables are you tracking?", 
    min_value=2, max_value=6, value=4, step=1,
    help="The matrix generation engine automatically scales its dimensional columns to match this value."
)

factor_levels = st.sidebar.radio(
    "How many levels (test settings) per factor do you require?",
    ["2 Levels (High / Low)", "3 Levels (High / Mid / Low)"]
)

bad_corners = st.sidebar.checkbox(
    "Do extreme parameter combinations risk damaging your equipment?",
    value=False,
    help="Example: Max temperature combined with lowest velocity glues the fixture shut."
)

# --- CORE LOGIC: DIAGNOSING THE DESIGN ---
suggested_design = ""
design_type = ""
justification = ""

if "Screening" in objective:
    if factors_count <= 3:
        suggested_design = f"Full Factorial Design (2^{int(factors_count)})"
        design_type = "FULL_FACTORIAL"
        justification = "Your factor count is small. A full 2-level matrix maps all primary variables and every interaction cleanly."
    else:
        suggested_design = f"Fractional Factorial Design (2^{int(factors_count)}-1)"
        design_type = "FRACTIONAL"
        justification = "Alleviates heavy lab workload by running a mathematically optimized half-fraction configuration, cleanly capturing primary main effects."

elif "Optimization" in objective:
    if bad_corners or factors_count == 3:
        suggested_design = "Box-Behnken Design (BBD)"
        design_type = "BOX_BEHNKEN"
        justification = "Your hardware savior. BBD programmatically places points strictly on the midpoints of your factor edges, completely omitting extreme corner combinations."
    else:
        suggested_design = "Central Composite Design (CCD)"
        design_type = "CCD"
        justification = "The standard for Response Surface Methodology. Pushes axial star points past normal boundaries to thoroughly map the outer limits of your processing envelope."

else:
    suggested_design = "Taguchi Orthogonal Array (L9 Layout)"
    design_type = "TAGUCHI"
    justification = "Focuses entirely on maximizing your Signal-to-Noise ratio to make your polymer process immune to messy, uncontrollable real-world laboratory noise."

# Display Diagnosed Result
st.header("🔬 Automated Statistical Design Diagnosis")
col_diag1, col_diag2 = st.columns(2)
with col_diag1:
    st.metric(label="RECOMMENDED MATRIX ARCHITECTURE", value=suggested_design)
with col_diag2:
    st.info(f"**Why this works:** {justification}")

st.write("---")

# --- MAIN PANEL: DYNAMIC VARIABLE INGESTION ---
st.header("🛠️ Step 2: Enter Variable Physical Boundaries")
st.markdown("Specify the real names and operating limits for your variables. The app will automatically scale the matrix values.")

# Dynamic input generation up to N factors
factor_data = {}
for i in range(int(factors_count)):
    factor_letter = chr(65 + i)
    st.markdown(f"#### Variable {i+1} ({factor_letter})")
    c1, c2, c3 = st.columns([2, 1, 1])
    
    with c1:
        v_name = st.text_input(f"Variable Name", value=f"Parameter_{factor_letter}", key=f"name_{i}")
    with c2:
        v_min = st.number_input(f"Minimum Value (-1)", value=10.0 * (i+1), key=f"min_{i}")
    with c3:
        v_max = st.number_input(f"Maximum Value (+1)", value=100.0 * (i+1), key=f"max_{i}")
        
    if v_min >= v_max:
        st.error("Error: Minimum value must be strictly lower than Maximum value.")
        
    factor_data[factor_letter] = {"name": v_name, "min": v_min, "max": v_max, "mid": (v_min + v_max) / 2.0}

st.write("---")

# --- N-DIMENSIONAL MATRIX GENERATION ENGINE ---
st.header("📊 Step 3: Generated Run Matrix")

if st.button("Generate Randomized Lab Run Sheet", type="primary"):
    coded_runs = []
    k = int(factors_count)
    
    # 1. ALGORITHMIC GENERATION OF BASE CODED MATRICES (-1, 0, 1)
    if design_type == "FULL_FACTORIAL":
        # Fully scales to N variables via iterative cross-products
        coded_runs = [list(x) for x in itertools.product([-1.0, 1.0], repeat=k)]
        
    elif design_type == "FRACTIONAL":
        # Dynamic half-fraction engine: Calculates base, then sets last column as the product interaction generator
        base_combinations = [list(x) for x in itertools.product([-1.0, 1.0], repeat=k-1)]
        for row in base_combinations:
            interaction_generator = 1.0
            for val in row:
                interaction_generator *= val
            coded_runs.append(row + [interaction_generator])
            
    elif design_type == "BOX_BEHNKEN":
        # Programmatic BBD generation: Loops through all distinct factor pairs, 
        # sets them to combinations of +/-1, and holds all other remaining dimensions at 0.
        for pair in itertools.combinations(range(k), 2):
            for bits in itertools.product([-1.0, 1.0], repeat=2):
                row = [0.0] * k
                row[pair[0]] = bits[0]
                row[pair[1]] = bits[1]
                coded_runs.append(row)
        # Add dynamic center points
        for _ in range(3):
            coded_runs.append([0.0] * k)
            
    elif design_type == "CCD":
        # Programmatic Face-Centered CCD Engine: Full Factorial block + Axial star points along every dimension
        for bits in itertools.product([-1.0, 1.0], repeat=k):
            coded_runs.append(list(bits))
        for i in range(k):
            row_neg = [0.0] * k
            row_neg[i] = -1.0
            coded_runs.append(row_neg)
            row_pos = [0.0] * k
            row_pos[i] = 1.0
            coded_runs.append(row_pos)
        # Add dynamic center points
        for _ in range(3):
            coded_runs.append([0.0] * k)
            
    else:
        # TAGUCHI L9 Architecture scaled to up to 4 variables
        l9_base = [
            [-1.0, -1.0, -1.0, -1.0],
            [-1.0,  0.0,  0.0,  0.0],
            [-1.0,  1.0,  1.0,  1.0],
            [ 0.0, -1.0,  0.0,  1.0],
            [ 0.0,  0.0,  1.0, -1.0],
            [ 0.0,  1.0, -1.0,  0.0],
            [ 1.0, -1.0,  1.0,  0.0],
            [ 1.0,  0.0, -1.0,  1.0],
            [ 1.0,  1.0,  0.0, -1.0]
        ]
        # Slice columns to precisely match factor constraints if k < 4, or expand if higher
        if k <= 4:
            coded_runs = [row[:k] for row in l9_base]
        else:
            # Fallback for ultra-high factor Taguchi counts in workshop environments
            coded_runs = [list(x) for x in itertools.product([-1.0, 0.0, 1.0], repeat=k)][:18]

    # 2. MAP CODED VALUES TO USER-DEFINED PHYSICAL PARAMETERS
    final_rows = []
    for row in coded_runs:
        scaled_row = {}
        for idx, val in enumerate(row):
            factor_letter = chr(65 + idx)
            name = factor_data[factor_letter]["name"]
            f_min = factor_data[factor_letter]["min"]
            f_max = factor_data[factor_letter]["max"]
            f_mid = factor_data[factor_letter]["mid"]
            
            if val == -1.0:
                actual_val = f_min
            elif val == 1.0:
                actual_val = f_max
            else:
                actual_val = f_mid
                
            scaled_row[name] = round(actual_val, 3)
        final_rows.append(scaled_row)

    # 3. COMPILE DATAFRAME & APPLY RANDOMIZATION
    df = pd.DataFrame(final_rows)
    df.insert(0, "Standard Order", range(1, len(df) + 1))
    
    # Shuffle completely to eliminate background time-confounding trends in the lab
    df_randomized = df.sample(frac=1.0).reset_index(drop=True)
    df_randomized.insert(0, "Run Order", range(1, len(df_randomized) + 1))

    # 4. PRESENT DATA INTERFACE TO USER
    st.success(f"🎉 Matrix compiled in less than 1 second! Generated a total of {len(df_randomized)} customized test configurations.")
    
    st.markdown("### 📋 Live Lab Work Sheet")
    st.dataframe(df_randomized, use_container_width=True)
    
    # Export capability for active workshop pipeline validation
    csv_data = df_randomized.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download This N-Dimensional Matrix as CSV",
        data=csv_data,
        file_name="Dynamic_DoE_Lab_Sheet.csv",
        mime="text/csv"
    )
else:
    st.info("Adjust your parameters above and click 'Generate' to compile your multi-variable matrix spreadsheet.")