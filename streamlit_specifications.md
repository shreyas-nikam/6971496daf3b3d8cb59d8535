
# Streamlit Application Specification: Agent Runtime Constraint Simulator

## 1. Application Overview

This application, "Agent Runtime Constraint Simulator," is designed for Platform Engineers like Alex at QuantAlgo Solutions. Its primary purpose is to operationalize agentic AI risk control by providing a simulated environment where autonomous AI agents operate under explicit runtime constraints, policies, and approvals. The application allows Alex to define agent capabilities (tools), configure granular policies (e.g., budget limits, approval gates), design test scenarios, run simulations, and meticulously audit agent behavior.

The high-level story flow is as follows:

1.  **Initialize/Configure:** The Platform Engineer (Alex) starts by loading or defining the agent's available tools in the **Tool Registry Editor**, then configures its operational policies (e.g., allowed tools, max steps, budget, approval rules) in the **Policy Editor**.
2.  **Design Test Cases:** Alex then defines various tasks for the agent in the **Task Runner**, including scenarios expected to succeed, trigger policy violations, or require explicit human approval.
3.  **Simulate & Observe:** Alex initiates the simulation for the defined tasks. The application's core policy engine enforces all rules at every step, transitioning the agent through states like `PLAN`, `ACT`, `APPROVAL_REQUIRED`, or `VIOLATION`.
4.  **Audit & Report:** After the simulation, Alex reviews the **Execution Trace Viewer** for detailed step-by-step logs and the **Violation Summary** for detected policy breaches. Finally, an **Export Panel** allows for the generation and download of audit-grade reports and artifacts, complete with SHA-256 hashes for integrity verification, providing concrete evidence of compliance and safety.

This workflow directly addresses the enterprise question: "Can this agent be trusted to act autonomously without violating safety, cost, or authorization boundaries—and can we audit every step it takes?" by demonstrating deterministic, policy-constrained execution and comprehensive audit trails.

## 2. Code Requirements

### Import Statement

```python
import streamlit as st
import json
import os
import shutil
import base64
from source import * # Import all functions and classes from source.py
```

### Streamlit Session State (`st.session_state`) Design

The `st.session_state` is crucial for maintaining data across user interactions and page changes.

*   **Initialization (on first run):**
    *   `st.session_state.setdefault('openai_api_key', '')`
    *   `st.session_state.setdefault('tool_registry', [])`
    *   `st.session_state.setdefault('agent_policy', {})`
    *   `st.session_state.setdefault('task_definitions', [])`
    *   `st.session_state.setdefault('execution_trace', [])`
    *   `st.session_state.setdefault('violations_summary', [])`
    *   `st.session_state.setdefault('run_id', None)`
    *   `st.session_state.setdefault('current_run_output_dir', None)`
    *   `st.session_state.setdefault('page', 'Overview')`

*   **`st.session_state` Keys and Usage:**

    *   `openai_api_key` (string): Stores the user-provided OpenAI API key from the sidebar. **Initialized:** To an empty string. **Updated:** By `st.sidebar.text_input`. **Read:** Accessed by other components if LLM integration were present (not directly used by `source.py` in this version).
    *   `tool_registry` (list of dicts): Stores the current tool definitions.
        *   **Initialized:** When "Initialize/Reset Data" is clicked, by loading `sample_tool_registry.json` after `create_tool_registry` is called.
        *   **Updated:** When the user modifies entries in the `st.data_editor` or adds new tools in the "Tool Registry Editor" page.
        *   **Read:** Used by `PolicyEngine` and `AgentSimulator` during simulation, and displayed in the "Tool Registry Editor".
    *   `agent_policy` (dict): Stores the current agent policy configuration.
        *   **Initialized:** When "Initialize/Reset Data" is clicked, by loading `sample_agent_policy.json` after `create_agent_policy` is called.
        *   **Updated:** When the user modifies policy settings via `st.multiselect`, `st.number_input`, `st.text_input` in the "Policy Editor" page.
        *   **Read:** Used by `PolicyEngine` and `AgentSimulator` during simulation, and displayed in the "Policy Editor".
    *   `task_definitions` (list of dicts): Stores the current task definitions for simulation.
        *   **Initialized:** When "Initialize/Reset Data" is clicked, by loading `sample_task_definitions.json` after `create_task_definitions` is called.
        *   **Updated:** When the user modifies entries in the `st.data_editor` or adds new tasks in the "Task Runner" page.
        *   **Read:** Used by `AgentSimulator` during simulation, and displayed in the "Task Runner".
    *   `execution_trace` (list of dicts): Stores the detailed log of the agent's actions and policy decisions from the last simulation run.
        *   **Initialized:** To an empty list.
        *   **Updated:** After a simulation run by calling `simulator.run_all_tasks()` and `simulator.execution_trace` is assigned.
        *   **Read:** Displayed in the "Simulation & Results" page.
    *   `violations_summary` (list of dicts): Stores a summary of all detected policy violations and approval requirements from the last simulation run.
        *   **Initialized:** To an empty list.
        *   **Updated:** After a simulation run by calling `simulator.run_all_tasks()` and `simulator.violations_summary` is assigned.
        *   **Read:** Displayed in the "Simulation & Results" page.
    *   `run_id` (string): Unique identifier for the last simulation run.
        *   **Initialized:** To `None`.
        *   **Updated:** After a simulation run by `simulator.run_id`.
        *   **Read:** Displayed in "Simulation & Results" and "Export Panel".
    *   `current_run_output_dir` (string): Path to the directory containing artifacts for the last simulation run.
        *   **Initialized:** To `None`.
        *   **Updated:** After a simulation run by `simulator.current_run_output_dir`.
        *   **Read:** Used in "Export Panel" to locate artifacts for zipping.
    *   `page` (string): Controls the current view in the multi-page simulation.
        *   **Initialized:** To `'Overview'`.
        *   **Updated:** By `st.sidebar.selectbox` selection.
        *   **Read:** Determines which content block is rendered.

### UI Interactions and `source.py` Function Invocations

#### Sidebar

```python
st.sidebar.markdown(f"## Configuration")
st.session_state['openai_api_key'] = st.sidebar.text_input("OpenAI API Key (Optional)", type="password", value=st.session_state['openai_api_key'])

st.sidebar.markdown(f"---")
st.sidebar.markdown(f"## Navigation")
st.session_state['page'] = st.sidebar.selectbox(
    "Choose a Section",
    ["Overview", "Tool Registry Editor", "Policy Editor", "Task Runner", "Simulation & Results", "Export Panel"]
)

st.sidebar.markdown(f"---")
st.sidebar.markdown(f"## Data Management")
if st.sidebar.button("Initialize/Reset Sample Data"):
    # Clear existing data and create sample files
    create_tool_registry(tool_registry_path)
    create_agent_policy(agent_policy_path)
    create_task_definitions(task_definitions_path)

    # Load into session state
    with open(tool_registry_path, 'r') as f:
        st.session_state['tool_registry'] = json.load(f)
    with open(agent_policy_path, 'r') as f:
        st.session_state['agent_policy'] = json.load(f)
    with open(task_definitions_path, 'r') as f:
        st.session_state['task_definitions'] = json.load(f)

    # Reset simulation results
    st.session_state['execution_trace'] = []
    st.session_state['violations_summary'] = []
    st.session_state['run_id'] = None
    st.session_state['current_run_output_dir'] = None

    st.sidebar.success("Sample data initialized!")
    st.session_state['page'] = 'Overview' # Navigate to overview after reset
    st.rerun() # Rerun to update content
```

#### 1. Overview Page

```python
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
    st.markdown(f"This lab treats agents as stateful systems, not prompts with loops.")
```

#### 2. Tool Registry Editor Page

```python
if st.session_state['page'] == "Tool Registry Editor":
    st.markdown(f"# 3. Building the Agent's Arsenal: Defining the Tool Registry")
    st.markdown(f"The Market Data Analyst Agent at QuantAlgo Solutions will interact with several internal and external tools. As a Platform Engineer, I need to define each tool meticulously, detailing its purpose, access level, and associated risk. This registry will serve as the definitive list of tools our agent is allowed to *know about*. Each tool will also have a `mock_function` to simulate its actual behavior without making real API calls.")
    st.markdown(f"For instance, a 'MarketDataAPI_Read' tool would be `read-only` and `low` risk, while a 'Portfolio_Update' tool would be `write` and `critical` risk. This distinction is crucial for setting up our guardrails.")

    st.markdown(r"$$\text{{Authorization Matrix}} = \begin{{bmatrix}}T_1 & A(T_1) & R(T_1) \\T_2 & A(T_2) & R(T_2) \\\vdots & \vdots & \vdots \\T_N & A(T_N) & R(T_N) \\ \end{{bmatrix}}$$")
    st.markdown(r"where $T_i$ represents tool $i$, $A(T_i)$ is its access level, and $R(T_i)$ is its risk class.")

    st.markdown(f"The purpose of defining this registry is to establish the base capabilities and inherent risks of each function the agent might invoke. This forms the first layer of our security model.")
    st.markdown(f"---")

    st.markdown(f"### Current Tool Registry")
    if st.session_state['tool_registry']:
        # Display editable tool registry
        edited_tool_registry = st.data_editor(
            st.session_state['tool_registry'],
            num_rows="dynamic",
            use_container_width=True,
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
            # Optionally, you might want to save this back to a temp file here if the simulator needs to read it
            # For simplicity, the simulator will use the session state directly.
    else:
        st.info("Tool registry is empty. Please initialize sample data or add tools.")
```

#### 3. Policy Editor Page

```python
if st.session_state['page'] == "Policy Editor":
    st.markdown(f"# 4. Laying Down the Law: Crafting Agent Execution Policies")
    st.markdown(f"Now that we know what tools our agent *can* potentially use, it's time to define the strict rules it *must* follow. As a Platform Engineer, I configure the `agent_policy.json` to enforce critical guardrails like allowed tools, maximum execution steps, budget limits (representing cost in tokens or compute), and explicit approval gates for sensitive operations.")
    st.markdown(f"This policy is the cornerstone of our agent's safe operation. Without it, an autonomous agent could easily spiral out of control, incurring excessive costs or performing unauthorized actions. For instance, we'll ensure the Market Data Analyst Agent cannot access the `System_Config_Change` tool, and any `Portfolio_Update` action requires explicit human approval due to its `critical` risk class.")

    st.markdown(r"$$\text{{Policy Function}} P(action, state) \rightarrow \text{{Decision}} \in \{\text{{Approved, Denied, Approval Required}}\}$$")
    st.markdown(r"where the decision is based on conditions like tool permission, step limit, budget limit, and approval gate checks.")
    st.markdown(r"The decision is based on a set of logical conditions:")
    st.markdown(r"*   **Tool Permission Check:** Is $T_{\text{{proposed}}} \in T_{\text{{allowed}}}$?")
    st.markdown(r"*   **Step Limit Check:** Is $S_{\text{{current}}} < S_{\text{{max}}}$?")
    st.markdown(r"*   **Budget Limit Check:** Is $C_{\text{{action}}} + C_{\text{{current}}} \leq C_{\text{{max}}}$?")
    st.markdown(r"*   **Approval Gate Check:** Is $R(T_{\text{{proposed}}}) \geq R_{\text{{threshold}}}$ or $A(T_{\text{{proposed}}}) \in A_{\text{{approval\_required}}}$?")

    st.markdown(f"If any of these conditions are not met, a violation or approval requirement is triggered.")
    st.markdown(f"---")

    st.markdown(f"### Current Agent Policy Configuration")
    if st.session_state['agent_policy']:
        current_policy = st.session_state['agent_policy']

        # Allowed Tools
        all_available_tools = [tool['tool_name'] for tool in st.session_state['tool_registry']]
        current_policy['allowed_tools'] = st.multiselect(
            "Allowed Tools",
            options=all_available_tools,
            default=current_policy.get('allowed_tools', []),
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
        # Approval Required for Access Levels
        current_policy['approval_required_for']['access_levels'] = st.multiselect(
            "Approval Required for Access Levels",
            options=["read-only", "write", "execute"],
            default=current_policy.get('approval_required_for', {}).get('access_levels', []),
            key="policy_approval_access_levels"
        )

        # Approval Required for Risk Classes
        current_policy['approval_required_for']['risk_classes'] = st.multiselect(
            "Approval Required for Risk Classes",
            options=["low", "medium", "high", "critical"],
            default=current_policy.get('approval_required_for', {}).get('risk_classes', []),
            key="policy_approval_risk_classes"
        )

        # Escalation Rule
        current_policy['escalation_rule'] = st.text_input(
            "Escalation Rule (e.g., Notify Security Team)",
            value=current_policy.get('escalation_rule', "Notify Security Team and Terminate Agent"),
            key="policy_escalation_rule"
        )

        if st.button("Update Agent Policy"):
            st.session_state['agent_policy'] = current_policy
            st.success("Agent policy updated in session state!")
    else:
        st.info("Agent policy is empty. Please initialize sample data.")
```

#### 4. Task Runner Page

```python
if st.session_state['page'] == "Task Runner":
    st.markdown(f"# 5. Designing Test Scenarios: Defining Agent Tasks")
    st.markdown(f"With our tools and policies in place, the next crucial step is to define specific tasks for our agent to perform in the simulation. These `task_definitions.json` are not just random assignments; they are carefully crafted test cases designed to validate our policies under different conditions. As a Platform Engineer, I need to ensure these tasks will trigger:")
    st.markdown(f"1.  A standard, compliant execution.")
    st.markdown(f"2.  A policy violation (e.g., attempting a disallowed tool or exceeding limits).")
    st.markdown(f"3.  A scenario requiring explicit human approval.")
    st.markdown(f"This strategic task definition is key to thoroughly stress-testing our guardrails.")
    st.markdown(f"---")

    st.markdown(f"### Current Task Definitions")
    if st.session_state['task_definitions']:
        # Data editor for tasks
        edited_tasks = st.data_editor(
            st.session_state['task_definitions'],
            num_rows="dynamic",
            use_container_width=True,
            key="task_definitions_editor",
            column_config={
                "task_id": st.column_config.TextColumn("Task ID", required=True),
                "task_description": st.column_config.TextColumn("Description", required=True),
                "expected_actions": st.column_config.JsonColumn(
                    "Expected Actions (JSON Array)",
                    help="e.g., [{\"tool_name\": \"MarketDataAPI_Read\", \"params\": {\"query\": \"tech stock trends\"}, \"cost\": 10}]",
                    min_width=200, required=True
                ),
                "expected_outcome": st.column_config.TextColumn("Expected Outcome")
            }
        )
        if st.button("Update Task Definitions"):
            st.session_state['task_definitions'] = edited_tasks
            st.success("Task definitions updated in session state!")
    else:
        st.info("Task definitions are empty. Please initialize sample data or add tasks.")

    st.markdown(f"---")
    st.markdown(f"### Run Simulation")
    if st.button("Run Agent Simulation", type="primary"):
        if not st.session_state['tool_registry'] or not st.session_state['agent_policy'] or not st.session_state['task_definitions']:
            st.error("Please ensure Tool Registry, Agent Policy, and Task Definitions are loaded/configured before running.")
        else:
            with st.spinner("Running agent simulation... This may take a moment."):
                # Need to ensure MOCK_TOOL_FUNCTIONS is populated, which happens when create_tool_registry is called.
                # Since we rely on sample data, it should be ok if "Initialize/Reset Data" was used.
                # If users manually edit, new mock_function_name might not exist in MOCK_TOOL_FUNCTIONS.
                # For this blueprint, assume the user maintains valid mock function names as per initial samples.

                # Re-create the sample files so the simulator can read from expected paths if needed
                # However, the AgentSimulator constructor directly takes the dicts, so we pass session state.
                # The create_* functions mainly serve to *generate* the initial files and populate global MOCK_TOOL_FUNCTIONS.
                
                # To ensure MOCK_TOOL_FUNCTIONS is correctly populated, call create_tool_registry again.
                # This is a bit of a hack around the global variable design in source.py for UI edits.
                # In a real app, mock_tool_functions would be part of PolicyEngine or simulator initialization.
                create_tool_registry(tool_registry_path) # Populates MOCK_TOOL_FUNCTIONS

                simulator = AgentSimulator(
                    st.session_state['tool_registry'],
                    st.session_state['agent_policy'],
                    st.session_state['task_definitions']
                )
                simulator.run_all_tasks()
                simulator.save_artifacts() # This will save to OUTPUT_DIR/<run_id>/

                st.session_state['execution_trace'] = simulator.execution_trace
                st.session_state['violations_summary'] = simulator.violations_summary
                st.session_state['run_id'] = simulator.run_id
                st.session_state['current_run_output_dir'] = simulator.current_run_output_dir

            st.success(f"Simulation complete! Run ID: `{st.session_state['run_id']}`. Navigate to 'Simulation & Results' to view findings.")
            st.session_state['page'] = 'Simulation & Results' # Auto-navigate
            st.rerun()
```

#### 5. Simulation & Results Page

```python
if st.session_state['page'] == "Simulation & Results":
    st.markdown(f"# 6. The Policy Enforcer: Implementing the Agent State Machine & Policy Engine")
    st.markdown(f"This is the engineering core of our validation. As a Platform Engineer, I need to implement a robust `AgentSimulator` that models the agent's behavior as a deterministic state machine. Crucially, before *each* simulated action, a `PolicyEngine` must intercede to check for violations against our defined `agent_policy.json` and `tool_registry.json`.")
    st.markdown(f"The agent will transition through states like `INIT`, `PLAN`, `ACT`, `REVIEW`, `APPROVAL_REQUIRED`, `COMPLETE`, or `VIOLATION`. This state machine ensures every decision and its outcome is traceable.")

    st.markdown(r"$$\text{{State Transition Function}} \delta(S_t, A_t, P_{\text{{outcome}}})$$")
    st.markdown(r"where $S_t$ is the current state, $A_t$ is the proposed action, and $P_{\text{{outcome}}}$ is the policy engine's decision.")
    st.markdown(r"For each step $t$:")
    st.markdown(r"1.  Agent proposes action $A_t$.")
    st.markdown(r"2.  Policy Engine evaluates $P(A_t, S_t) \rightarrow P_{\text{{outcome}}}$.")
    st.markdown(r"3.  New state $S_{\text{{t+1}}} = \delta(S_t, A_t, P_{\text{{outcome}}})$.")
    st.markdown(r"Example transitions:")
    st.markdown(r"*   If $P_{\text{{outcome}}} = \text{{APPROVED}}$, then $S_{\text{{t+1}}} = \text{{ACT}}$.")
    st.markdown(r"*   If $P_{\text{{outcome}}} = \text{{REQUIRES\_APPROVAL}}$, then $S_{\text{{t+1}}} = \text{{APPROVAL\_REQUIRED}}$.")
    st.markdown(r"*   If $P_{\text{{outcome}}} = \text{{DENIED\_VIOLATION}}$, then $S_{\text{{t+1}}} = \text{{VIOLATION}}$.")
    st.markdown(r"The `PolicyEngine` also tracks resource consumption (steps, budget). For budget, if $C_{\text{{action}}}$ is the cost of the proposed action and $B_{\text{{current}}}$ is the remaining budget, the new budget $B_{\text{{next}}} = B_{\text{{current}}} - C_{\text{{action}}}$. A violation occurs if $B_{\text{{next}}} < 0$. Similarly for steps, if $S_{\text{{current}}}$ is the current step count and $S_{\text{{max}}}$ is the maximum, a violation occurs if $S_{\text{{current}}} + 1 > S_{\text{{max}}}$.")

    st.markdown(f"---")
    st.markdown(f"# 7. Putting Policies to the Test: Running Simulations and Tracing Decisions")
    st.markdown(f"Now comes the moment of truth. As a Platform Engineer, I will instantiate our `AgentSimulator` with the tools, policies, and tasks we defined. Then, I will execute all the tasks to see how our agent behaves under the policy engine's strict supervision. Every step, every policy decision, and every state transition will be logged to an `execution_trace.json`, providing an audit-grade record of the agent's constrained execution.")
    st.markdown(f"This hands-on execution demonstrates how our theoretical policies translate into real-world (simulated) enforcement, providing critical feedback on the robustness of our guardrails.")
    st.markdown(f"---")

    st.markdown(f"# 8. Auditing Agent Behavior: Analyzing Violations and Generating Reports")
    st.markdown(f"The simulation generated a wealth of data about the agent's behavior. My job as a Platform Engineer doesn't end with running the simulation; I must analyze the results, particularly the `violations_summary.json` and `execution_trace.json`, to confirm that policies were correctly enforced.")
    st.markdown(f"This step involves reviewing the audit logs to confirm that:")
    st.markdown(f"1.  Compliant actions proceeded without hindrance.")
    st.markdown(f"2.  Disallowed tool usage was correctly identified and stopped.")
    st.markdown(f"3.  Budget and step limits were enforced.")
    st.markdown(f"4.  Sensitive operations correctly triggered an `APPROVAL_REQUIRED` state.")
    st.markdown(f"Finally, I will generate a comprehensive `session09_executive_summary.md` report and an `evidence_manifest.json` (with SHA-256 hashes for integrity), providing concrete proof to stakeholders that the agent is ready for deployment. This output is our deliverable, ensuring auditability and confidence in the agent's safety.")
    st.markdown(f"---")


    st.markdown(f"### Simulation Results for Run ID: `{st.session_state['run_id'] if st.session_state['run_id'] else 'N/A'}`")

    if st.session_state['execution_trace']:
        st.markdown(f"#### Execution Trace")
        st.dataframe(st.session_state['execution_trace'], use_container_width=True)
    else:
        st.info("No simulation has been run yet or trace is empty. Please configure tasks and run the simulation.")

    if st.session_state['violations_summary']:
        st.markdown(f"#### Violation Summary")
        st.dataframe(st.session_state['violations_summary'], use_container_width=True)
    else:
        st.success("No violations or approval requirements detected in the last simulation run.")
```

#### 6. Export Panel Page

```python
if st.session_state['page'] == "Export Panel":
    st.markdown(f"# 9. Output Artifacts")
    st.markdown(f"All generated output artifacts are stored in a run-specific directory within `reports/session09/`.")
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
    st.markdown(f"All artifacts within the evidence manifest are hashed with SHA-256 to ensure data integrity and auditability.")
    st.markdown(f"---")

    if st.session_state['current_run_output_dir'] and os.path.exists(st.session_state['current_run_output_dir']):
        st.markdown(f"### Last Simulation Output (Run ID: `{st.session_state['run_id']}`)")
        st.markdown(f"Artifacts located at: `{st.session_state['current_run_output_dir']}`")

        # Create a zip archive of the output directory
        zip_file_name = f"Session_09_{st.session_state['run_id']}"
        zip_path = shutil.make_archive(
            os.path.join(OUTPUT_DIR, zip_file_name), # Base name for the archive
            'zip',                                 # Archive format
            st.session_state['current_run_output_dir'] # Directory to archive
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
        
        st.success(f"All artifacts for run `{st.session_state['run_id']}` bundled and ready for download.")

        # Display executive summary content directly
        executive_summary_path = os.path.join(st.session_state['current_run_output_dir'], "session09_executive_summary.md")
        if os.path.exists(executive_summary_path):
            st.markdown(f"#### Executive Summary (`session09_executive_summary.md`)")
            with open(executive_summary_path, 'r') as f:
                st.code(f.read(), language='markdown')

        # Display evidence manifest content directly
        evidence_manifest_path = os.path.join(st.session_state['current_run_output_dir'], "evidence_manifest.json")
        if os.path.exists(evidence_manifest_path):
            st.markdown(f"#### Evidence Manifest (`evidence_manifest.json`)")
            with open(evidence_manifest_path, 'r') as f:
                st.json(json.load(f))

    else:
        st.info("No simulation results available for export. Please run a simulation first.")
```
