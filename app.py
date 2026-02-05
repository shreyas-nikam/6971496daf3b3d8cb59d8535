import streamlit as st
import json
import os
import shutil
import base64
from source import *

# Page Configuration
st.set_page_config(
    page_title="QuLab: Lab 9: Agent Runtime Constraint Simulator", layout="wide")

# Sidebar Header
st.sidebar.image("https://www.quantuniversity.com/assets/img/logo5.jpg")
st.sidebar.divider()

# Main Title
st.title("QuLab: Lab 9: Agent Runtime Constraint Simulator")
st.divider()

# --- Session State Initialization ---
if 'openai_api_key' not in st.session_state:
    st.session_state['openai_api_key'] = ''
if 'tool_registry' not in st.session_state:
    st.session_state['tool_registry'] = []
if 'agent_policy' not in st.session_state:
    st.session_state['agent_policy'] = {}
if 'task_definitions' not in st.session_state:
    st.session_state['task_definitions'] = []
if 'execution_trace' not in st.session_state:
    st.session_state['execution_trace'] = []
if 'violations_summary' not in st.session_state:
    st.session_state['violations_summary'] = []
if 'run_id' not in st.session_state:
    st.session_state['run_id'] = None
if 'current_run_output_dir' not in st.session_state:
    st.session_state['current_run_output_dir'] = None
if 'page' not in st.session_state:
    st.session_state['page'] = 'Overview'

# --- Sidebar Logic ---
st.sidebar.markdown(f"## Configuration")
st.session_state['openai_api_key'] = st.sidebar.text_input(
    "OpenAI API Key (Optional)", type="password", value=st.session_state['openai_api_key'])

st.sidebar.markdown(f"---")
st.sidebar.markdown(f"## Navigation")

# Navigation Selection
nav_options = ["Overview", "Tool Registry Editor", "Policy Editor",
               "Task Runner", "Simulation & Results", "Export Panel"]
try:
    current_index = nav_options.index(st.session_state['page'])
except ValueError:
    current_index = 0

selected_page = st.sidebar.selectbox(
    "Choose a Section",
    nav_options,
    index=current_index
)
st.session_state['page'] = selected_page

st.sidebar.markdown(f"---")
st.sidebar.markdown(f"## Data Management")

if st.sidebar.button("Initialize/Reset Sample Data"):
    # Clear existing data and create sample files via source.py functions
    create_tool_registry(tool_registry_path)
    create_agent_policy(agent_policy_path)
    create_task_definitions(task_definitions_path)

    # Load into session state
    if os.path.exists(tool_registry_path):
        with open(tool_registry_path, 'r') as f:
            st.session_state['tool_registry'] = json.load(f)
    if os.path.exists(agent_policy_path):
        with open(agent_policy_path, 'r') as f:
            st.session_state['agent_policy'] = json.load(f)
    if os.path.exists(task_definitions_path):
        with open(task_definitions_path, 'r') as f:
            st.session_state['task_definitions'] = json.load(f)

    # Reset simulation results
    st.session_state['execution_trace'] = []
    st.session_state['violations_summary'] = []
    st.session_state['run_id'] = None
    st.session_state['current_run_output_dir'] = None

    st.sidebar.success("Sample data initialized!")
    st.session_state['page'] = 'Overview'  # Navigate to overview after reset
    st.rerun()

# --- Page Content ---

# 1. Overview Page
if st.session_state['page'] == "Overview":
    st.markdown(f"# Lab 9: Agent Policy Sandbox & Guardrail Validation")
    st.markdown(f"## A Platform Engineer's Workflow")
    st.markdown(f"Welcome, fellow Platform Engineer! My name is Alex, and I work at QuantAlgo Solutions, a cutting-edge fintech firm. My primary responsibility is to ensure that our innovative AI agents operate within strict corporate governance, security, and financial controls. We're on the verge of deploying a new 'Market Data Analyst Agent' that will interact with various internal systems, but before it goes live, I need to thoroughly validate its runtime policies and guardrails. This involves setting up a secure, simulated environment, defining its operational boundaries, and then verifying that the agent adheres to these rules under different scenarios.")
    st.markdown(f"This application will walk us through the critical pre-deployment validation steps. We'll define the agent's available tools, configure its operational policies (like budget limits and approval gates), simulate its tasks, and meticulously audit its behavior. Our goal is to generate concrete evidence that the agent is safe, compliant, and ready for production.")
    st.markdown(f"---")
    st.markdown(f"### Purpose & Positioning")
    st.markdown(f"This lab operationalizes agentic AI risk control by simulating an autonomous agent operating under explicit runtime constraints, policies, and approvals.")
    st.markdown(f"It answers the enterprise question:")
    st.markdown(f"> Can this agent be trusted to act autonomously without violating safety, cost, or authorization boundaries—and can we audit every step it takes?")
    st.markdown(
        f"This lab treats agents as stateful systems, not prompts with loops.")

# 2. Tool Registry Editor Page
elif st.session_state['page'] == "Tool Registry Editor":
    st.markdown(f"# 3. Building the Agent's Arsenal: Defining the Tool Registry")
    st.markdown(f"The Market Data Analyst Agent at QuantAlgo Solutions will interact with several internal and external tools. As a Platform Engineer, I need to define each tool meticulously, detailing its purpose, access level, and associated risk. This registry will serve as the definitive list of tools our agent is allowed to *know about*. Each tool will also have a `mock_function` to simulate its actual behavior without making real API calls.")
    st.markdown(f"For instance, a 'MarketDataAPI_Read' tool would be `read-only` and `low` risk, while a 'Portfolio_Update' tool would be `write` and `critical` risk. This distinction is crucial for setting up our guardrails.")

    st.markdown(r"$$\text{Authorization Matrix} = \begin{bmatrix}T_1 & A(T_1) & R(T_1) \\T_2 & A(T_2) & R(T_2) \\\vdots & \vdots & \vdots \\T_N & A(T_N) & R(T_N) \\ \end{bmatrix}$$")
    st.markdown(
        r"where $T_i$ represents tool $i$, $A(T_i)$ is its access level, and $R(T_i)$ is its risk class.")

    st.markdown(f"The purpose of defining this registry is to establish the base capabilities and inherent risks of each function the agent might invoke. This forms the first layer of our security model.")
    st.markdown(f"---")

    st.markdown(f"### Current Tool Registry")
    if st.session_state['tool_registry']:
        # Display editable tool registry
        edited_tool_registry = st.data_editor(
            st.session_state['tool_registry'],
            num_rows="dynamic",
            width='stretch',
            key="tool_registry_editor",
            column_config={
                "tool_name": st.column_config.TextColumn("Tool Name", required=True),
                "description": st.column_config.TextColumn("Description", required=True),
                "access_level": st.column_config.SelectboxColumn(
                    "Access Level", options=["read-only", "write", "execute"], required=True
                ),
                "risk_class": st.column_config.SelectboxColumn(
                    "Risk Class", options=["low", "medium", "high", "critical"], required=True
                ),
                "mock_function_name": st.column_config.TextColumn("Mock Function Name", required=True)
            }
        )
        if st.button("Update Tool Registry"):
            st.session_state['tool_registry'] = edited_tool_registry
            st.success("Tool registry updated in session state!")
    else:
        st.info("Tool registry is empty. Please initialize sample data or add tools.")

# 3. Policy Editor Page
elif st.session_state['page'] == "Policy Editor":
    st.markdown(f"# 4. Laying Down the Law: Crafting Agent Execution Policies")
    st.markdown(f"Now that we know what tools our agent *can* potentially use, it's time to define the strict rules it *must* follow. As a Platform Engineer, I configure the `agent_policy.json` to enforce critical guardrails like allowed tools, maximum execution steps, budget limits (representing cost in tokens or compute), and explicit approval gates for sensitive operations.")
    st.markdown(f"This policy is the cornerstone of our agent's safe operation. Without it, an autonomous agent could easily spiral out of control, incurring excessive costs or performing unauthorized actions. For instance, we'll ensure the Market Data Analyst Agent cannot access the `System_Config_Change` tool, and any `Portfolio_Update` action requires explicit human approval due to its `critical` risk class.")

    st.markdown(
        r"$$\text{Policy Function} P(action, state) \rightarrow \text{Decision} \in \{\text{Approved, Denied, Approval Required}\}$$")
    st.markdown(
        r"where the decision is based on conditions like tool permission, step limit, budget limit, and approval gate checks.")
    st.markdown(r"The decision is based on a set of logical conditions:")
    st.markdown(
        r"*   **Tool Permission Check:** Is $T_{\text{proposed}} \in T_{\text{allowed}}$?")
    st.markdown(
        r"*   **Step Limit Check:** Is $S_{\text{current}} < S_{\text{max}}$?")
    st.markdown(
        r"*   **Budget Limit Check:** Is $C_{\text{action}} + C_{\text{current}} \leq C_{\text{max}}$?")
    st.markdown(
        r"*   **Approval Gate Check:** Is $R(T_{\text{proposed}}) \geq R_{\text{threshold}}$ or $A(T_{\text{proposed}}) \in A_{\text{approval\_required}}$?")

    st.markdown(
        f"If any of these conditions are not met, a violation or approval requirement is triggered.")
    st.markdown(f"---")

    st.markdown(f"### Current Agent Policy Configuration")
    if st.session_state['agent_policy']:
        current_policy = st.session_state['agent_policy']

        # Allowed Tools
        all_available_tools = [tool['tool_name']
                               for tool in st.session_state['tool_registry']]
        current_policy['allowed_tools'] = st.multiselect(
            "Allowed Tools",
            options=all_available_tools,
            default=[t for t in current_policy.get(
                'allowed_tools', []) if t in all_available_tools],
            key="policy_allowed_tools"
        )

        # Max Steps Per Run
        current_policy['max_steps_per_run'] = st.number_input(
            "Max Steps Per Run",
            min_value=1,
            value=current_policy.get('max_steps_per_run', 5),
            key="policy_max_steps"
        )

        # Budget Limit
        current_policy['budget_limit'] = st.number_input(
            "Budget Limit (e.g., tokens/cost proxy)",
            min_value=0,
            value=current_policy.get('budget_limit', 100),
            key="policy_budget_limit"
        )

        st.markdown(f"### Approval Requirements")

        # Initialize nested structure if missing
        if 'approval_required_for' not in current_policy:
            current_policy['approval_required_for'] = {
                'access_levels': [], 'risk_classes': []}

        # Approval Required for Access Levels
        current_policy['approval_required_for']['access_levels'] = st.multiselect(
            "Approval Required for Access Levels",
            options=["read-only", "write", "execute"],
            default=current_policy.get(
                'approval_required_for', {}).get('access_levels', []),
            key="policy_approval_access_levels"
        )

        # Approval Required for Risk Classes
        current_policy['approval_required_for']['risk_classes'] = st.multiselect(
            "Approval Required for Risk Classes",
            options=["low", "medium", "high", "critical"],
            default=current_policy.get(
                'approval_required_for', {}).get('risk_classes', []),
            key="policy_approval_risk_classes"
        )

        # Escalation Rule
        current_policy['escalation_rule'] = st.text_input(
            "Escalation Rule (e.g., Notify Security Team)",
            value=current_policy.get(
                'escalation_rule', "Notify Security Team and Terminate Agent"),
            key="policy_escalation_rule"
        )

        if st.button("Update Agent Policy"):
            st.session_state['agent_policy'] = current_policy
            st.success("Agent policy updated in session state!")
    else:
        st.info("Agent policy is empty. Please initialize sample data.")

# 4. Task Runner Page
elif st.session_state['page'] == "Task Runner":
    st.markdown(f"# 5. Designing Test Scenarios: Defining Agent Tasks")
    st.markdown(f"With our tools and policies in place, the next crucial step is to define specific tasks for our agent to perform in the simulation. These `task_definitions.json` are not just random assignments; they are carefully crafted test cases designed to validate our policies under different conditions. As a Platform Engineer, I need to ensure these tasks will trigger:")
    st.markdown(f"1.  A standard, compliant execution.")
    st.markdown(
        f"2.  A policy violation (e.g., attempting a disallowed tool or exceeding limits).")
    st.markdown(f"3.  A scenario requiring explicit human approval.")
    st.markdown(
        f"This strategic task definition is key to thoroughly stress-testing our guardrails.")
    st.markdown(f"---")

    st.markdown(f"### Current Task Definitions")
    if st.session_state['task_definitions']:
        # Data editor for tasks
        edited_tasks = st.data_editor(
            st.session_state['task_definitions'],
            num_rows="dynamic",
            width='stretch',
            key="task_definitions_editor",
            column_config={
                "task_id": st.column_config.TextColumn("Task ID", required=True),
                "task_description": st.column_config.TextColumn("Description", required=True),
                "expected_actions": st.column_config.JsonColumn(
                    "Expected Actions (JSON Array)",
                    help="e.g., [{\"tool_name\": \"MarketDataAPI_Read\", \"params\": {\"query\": \"tech stock trends\"}, \"cost\": 10}]"
                ),
                "expected_outcome": st.column_config.TextColumn("Expected Outcome")
            }
        )
        if st.button("Update Task Definitions"):
            st.session_state['task_definitions'] = edited_tasks
            st.success("Task definitions updated in session state!")
    else:
        st.info(
            "Task definitions are empty. Please initialize sample data or add tasks.")

    st.markdown(f"---")
    st.markdown(f"### Run Simulation")
    if st.button("Run Agent Simulation", type="primary"):
        if not st.session_state['tool_registry'] or not st.session_state['agent_policy'] or not st.session_state['task_definitions']:
            st.error(
                "Please ensure Tool Registry, Agent Policy, and Task Definitions are loaded/configured before running.")
        else:
            with st.spinner("Running agent simulation... This may take a moment."):
                # Re-create sample files to populate global MOCK_TOOL_FUNCTIONS in source.py
                create_tool_registry(tool_registry_path)

                simulator = AgentSimulator(
                    st.session_state['tool_registry'],
                    st.session_state['agent_policy'],
                    st.session_state['task_definitions']
                )
                simulator.run_all_tasks()
                simulator.save_artifacts()

                st.session_state['execution_trace'] = simulator.execution_trace
                st.session_state['violations_summary'] = simulator.violations_summary
                st.session_state['run_id'] = simulator.run_id
                st.session_state['current_run_output_dir'] = simulator.current_run_output_dir

            st.success(
                f"Simulation complete! Run ID: `{st.session_state['run_id']}`. Navigate to 'Simulation & Results' to view findings.")
            st.session_state['page'] = 'Simulation & Results'  # Auto-navigate
            st.rerun()

# 5. Simulation & Results Page
elif st.session_state['page'] == "Simulation & Results":
    st.markdown(
        f"# 6. The Policy Enforcer: Implementing the Agent State Machine & Policy Engine")
    st.markdown(f"This is the engineering core of our validation. As a Platform Engineer, I need to implement a robust `AgentSimulator` that models the agent's behavior as a deterministic state machine. Crucially, before *each* simulated action, a `PolicyEngine` must intercede to check for violations against our defined `agent_policy.json` and `tool_registry.json`.")
    st.markdown(f"The agent will transition through states like `INIT`, `PLAN`, `ACT`, `REVIEW`, `APPROVAL_REQUIRED`, `COMPLETE`, or `VIOLATION`. This state machine ensures every decision and its outcome is traceable.")

    st.markdown(
        r"$$\text{State Transition Function} \delta(S_t, A_t, P_{\text{outcome}})$$")
    st.markdown(
        r"where $S_t$ is the current state, $A_t$ is the proposed action, and $P_{\text{outcome}}$ is the policy engine's decision.")
    st.markdown(r"For each step $t$:")
    st.markdown(r"1.  Agent proposes action $A_t$.")
    st.markdown(
        r"2.  Policy Engine evaluates $P(A_t, S_t) \rightarrow P_{\text{outcome}}$.")
    st.markdown(
        r"3.  New state $S_{\text{t+1}} = \delta(S_t, A_t, P_{\text{outcome}})$.")
    st.markdown(r"Example transitions:")
    st.markdown(
        r"*   If $P_{\text{outcome}} = \text{APPROVED}$, then $S_{\text{t+1}} = \text{ACT}$.")
    st.markdown(
        r"*   If $P_{\text{outcome}} = \text{REQUIRES\_APPROVAL}$, then $S_{\text{t+1}} = \text{APPROVAL\_REQUIRED}$.")
    st.markdown(
        r"*   If $P_{\text{outcome}} = \text{DENIED\_VIOLATION}$, then $S_{\text{t+1}} = \text{VIOLATION}$.")
    st.markdown(r"The `PolicyEngine` also tracks resource consumption (steps, budget). For budget, if $C_{\text{action}}$ is the cost of the proposed action and $B_{\text{current}}$ is the remaining budget, the new budget $B_{\text{next}} = B_{\text{current}} - C_{\text{action}}$. A violation occurs if $B_{\text{next}} < 0$. Similarly for steps, if $S_{\text{current}}$ is the current step count and $S_{\text{max}}$ is the maximum, a violation occurs if $S_{\text{current}} + 1 > S_{\text{max}}$.")

    st.markdown(f"---")
    st.markdown(
        f"# 7. Putting Policies to the Test: Running Simulations and Tracing Decisions")
    st.markdown(f"Now comes the moment of truth. As a Platform Engineer, I will instantiate our `AgentSimulator` with the tools, policies, and tasks we defined. Then, I will execute all the tasks to see how our agent behaves under the policy engine's strict supervision. Every step, every policy decision, and every state transition will be logged to an `execution_trace.json`, providing an audit-grade record of the agent's constrained execution.")
    st.markdown(f"This hands-on execution demonstrates how our theoretical policies translate into real-world (simulated) enforcement, providing critical feedback on the robustness of our guardrails.")
    st.markdown(f"---")

    st.markdown(
        f"# 8. Auditing Agent Behavior: Analyzing Violations and Generating Reports")
    st.markdown(f"The simulation generated a wealth of data about the agent's behavior. My job as a Platform Engineer doesn't end with running the simulation; I must analyze the results, particularly the `violations_summary.json` and `execution_trace.json`, to confirm that policies were correctly enforced.")
    st.markdown(f"This step involves reviewing the audit logs to confirm that:")
    st.markdown(f"1.  Compliant actions proceeded without hindrance.")
    st.markdown(
        f"2.  Disallowed tool usage was correctly identified and stopped.")
    st.markdown(f"3.  Budget and step limits were enforced.")
    st.markdown(
        f"4.  Sensitive operations correctly triggered an `APPROVAL_REQUIRED` state.")
    st.markdown(f"Finally, I will generate a comprehensive `session09_executive_summary.md` report and an `evidence_manifest.json` (with SHA-256 hashes for integrity), providing concrete proof to stakeholders that the agent is ready for deployment. This output is our deliverable, ensuring auditability and confidence in the agent's safety.")
    st.markdown(f"---")

    st.markdown(
        f"### Simulation Results for Run ID: `{st.session_state['run_id'] if st.session_state['run_id'] else 'N/A'}`")

    if st.session_state['execution_trace']:
        st.markdown(f"#### Execution Trace")
        st.dataframe(
            st.session_state['execution_trace'], width='stretch')
    else:
        st.info(
            "No simulation has been run yet or trace is empty. Please configure tasks and run the simulation.")

    if st.session_state['violations_summary']:
        st.markdown(f"#### Violation Summary")
        st.dataframe(
            st.session_state['violations_summary'], width='stretch')
    else:
        st.success(
            "No violations or approval requirements detected in the last simulation run.")

# 6. Export Panel Page
elif st.session_state['page'] == "Export Panel":
    st.markdown(f"# 9. Output Artifacts")
    st.markdown(
        f"All generated output artifacts are stored in a run-specific directory within `reports/session09/`.")
    st.markdown(f"The following artifacts are produced:")
    st.markdown(f"- `tool_registry.json`")
    st.markdown(f"- `agent_policy.json`")
    st.markdown(f"- `execution_trace.json`")
    st.markdown(f"- `violations_summary.json`")
    st.markdown(f"- `session09_executive_summary.md`")
    st.markdown(f"- `config_snapshot.json`")
    st.markdown(f"- `evidence_manifest.json`")
    st.markdown(f"---")
    st.markdown(f"# 10. Evidence Manifest")
    st.markdown(
        f"All artifacts within the evidence manifest are hashed with SHA-256 to ensure data integrity and auditability.")
    st.markdown(f"---")

    if st.session_state['current_run_output_dir'] and os.path.exists(st.session_state['current_run_output_dir']):
        st.markdown(
            f"### Last Simulation Output (Run ID: `{st.session_state['run_id']}`)")
        st.markdown(
            f"Artifacts located at: `{st.session_state['current_run_output_dir']}`")

        # Create a zip archive of the output directory
        zip_file_name = f"Session_09_{st.session_state['run_id']}"
        # The simulator uses OUTPUT_DIR, we can reuse it if imported or construct path
        # Assuming OUTPUT_DIR is globally available from source.py or we just use path joining
        base_output_dir = os.path.dirname(
            st.session_state['current_run_output_dir'])

        zip_path = shutil.make_archive(
            # Base name for the archive
            os.path.join(base_output_dir, zip_file_name),
            'zip',                                 # Archive format
            st.session_state['current_run_output_dir']  # Directory to archive
        )

        with open(zip_path, "rb") as f:
            bytes_data = f.read()
            b64_zip = base64.b64encode(bytes_data).decode()
            href = f'<a href="data:application/zip;base64,{b64_zip}" download="{os.path.basename(zip_path)}">Download All Artifacts as .zip</a>'
            st.markdown(href, unsafe_allow_html=True)

            # Offer download button as an alternative for newer Streamlit versions
            st.download_button(
                label="Download Artifacts Zip",
                data=bytes_data,
                file_name=os.path.basename(zip_path),
                mime="application/zip",
            )

        st.success(
            f"All artifacts for run `{st.session_state['run_id']}` bundled and ready for download.")

        # Display executive summary content directly
        executive_summary_path = os.path.join(
            st.session_state['current_run_output_dir'], "session09_executive_summary.md")
        if os.path.exists(executive_summary_path):
            st.markdown(
                f"#### Executive Summary (`session09_executive_summary.md`)")
            with open(executive_summary_path, 'r') as f:
                st.code(f.read(), language='markdown')

        # Display evidence manifest content directly
        evidence_manifest_path = os.path.join(
            st.session_state['current_run_output_dir'], "evidence_manifest.json")
        if os.path.exists(evidence_manifest_path):
            st.markdown(f"#### Evidence Manifest (`evidence_manifest.json`)")
            with open(evidence_manifest_path, 'r') as f:
                st.json(json.load(f))

    else:
        st.info(
            "No simulation results available for export. Please run a simulation first.")


# License
st.caption('''
---
## QuantUniversity License

© QuantUniversity 2025  
This notebook was created for **educational purposes only** and is **not intended for commercial use**.  

- You **may not copy, share, or redistribute** this notebook **without explicit permission** from QuantUniversity.  
- You **may not delete or modify this license cell** without authorization.  
- This notebook was generated using **QuCreate**, an AI-powered assistant.  
- Content generated by AI may contain **hallucinated or incorrect information**. Please **verify before using**.  

All rights reserved. For permissions or commercial licensing, contact: [info@qusandbox.com](mailto:info@qusandbox.com)
''')
