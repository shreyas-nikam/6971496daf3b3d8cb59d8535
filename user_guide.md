id: 6971496daf3b3d8cb59d8535_user_guide
summary: Lab 9: Agent Runtime Constraint Simulator User Guide
feedback link: https://docs.google.com/forms/d/e/1FAIpQLSfWkOK-in_bMMoHSZfcIvAeO58PAH9wrDqcxnJABHaxiDqhSA/viewform?usp=sf_link
environments: Web
status: Published
# QuLab: Agent Runtime Constraint Simulator User Guide

## 1. Welcome to the Agent Policy Sandbox & Guardrail Validation
Duration: 00:05:00

Welcome, fellow Platform Engineer! My name is Alex, and I work at QuantAlgo Solutions, a cutting-edge fintech firm. My primary responsibility is to ensure that our innovative AI agents operate within strict corporate governance, security, and financial controls. We're on the verge of deploying a new 'Market Data Analyst Agent' that will interact with various internal systems, but before it goes live, I need to thoroughly validate its runtime policies and guardrails. This involves setting up a secure, simulated environment, defining its operational boundaries, and then verifying that the agent adheres to these rules under different scenarios.

This application will walk us through the critical pre-deployment validation steps. We'll define the agent's available tools, configure its operational policies (like budget limits and approval gates), simulate its tasks, and meticulously audit its behavior. Our goal is to generate concrete evidence that the agent is safe, compliant, and ready for production.

<aside class="positive">
<b>Important Context:</b> This lab operationalizes agentic AI risk control by simulating an autonomous agent operating under explicit runtime constraints, policies, and approvals. It answers the enterprise question: "Can this agent be trusted to act autonomously without violating safety, cost, or authorization boundaries—and can we audit every step it takes?" We treat agents as stateful systems, not just prompts with loops.
</aside>

Before we begin, you can optionally provide an OpenAI API Key in the sidebar. This key is not strictly necessary for the core simulation logic, as we use mock functions for tools, but it might be used for future enhancements involving actual LLM interactions.

To start with pre-configured sample data, click the "Initialize/Reset Sample Data" button in the sidebar. This will populate the Tool Registry, Policy Editor, and Task Runner with example configurations, making it easier to follow along.

## 2. Building the Agent's Arsenal: Defining the Tool Registry
Duration: 00:07:00

The Market Data Analyst Agent at QuantAlgo Solutions will interact with several internal and external tools. As a Platform Engineer, I need to define each tool meticulously, detailing its purpose, access level, and associated risk. This registry will serve as the definitive list of tools our agent is allowed to *know about*. Each tool will also have a `mock_function` to simulate its actual behavior without making real API calls.

For instance, a 'MarketDataAPI_Read' tool would be `read-only` and `low` risk, while a 'Portfolio_Update' tool would be `write` and `critical` risk. This distinction is crucial for setting up our guardrails.

The tool registry conceptually forms an authorization matrix:

$$\text{Authorization Matrix} = \begin{bmatrix}T_1 & A(T_1) & R(T_1) \\T_2 & A(T_2) & R(T_2) \\\vdots & \vdots & \vdots \\T_N & A(T_N) & R(T_N) \\ \end{bmatrix}$$

where $T_i$ represents tool $i$, $A(T_i)$ is its access level (e.g., 'read-only', 'write', 'execute'), and $R(T_i)$ is its risk class (e.g., 'low', 'medium', 'high', 'critical').

The purpose of defining this registry is to establish the base capabilities and inherent risks of each function the agent might invoke. This forms the first layer of our security model.

**How to Use:**
1.  Navigate to the "Tool Registry Editor" page using the sidebar navigation.
2.  You will see a data editor displaying the current tools. Each row represents a tool with columns for `tool_name`, `description`, `access_level`, `risk_class`, and `mock_function_name`.
3.  **To Add a Tool:** Scroll to the bottom of the table and click the `+ Add row` button. Fill in the details for the new tool.
4.  **To Edit a Tool:** Click on any cell in the table to modify its value. For `access_level` and `risk_class`, you can select from predefined options.
5.  **To Delete a Tool:** Hover over a row and click the trash can icon that appears on the left.
6.  Once you've made your changes, click the "Update Tool Registry" button below the table to save them to the application's session state.

## 3. Laying Down the Law: Crafting Agent Execution Policies
Duration: 00:08:00

Now that we know what tools our agent *can* potentially use, it's time to define the strict rules it *must* follow. As a Platform Engineer, I configure the agent's policy to enforce critical guardrails like allowed tools, maximum execution steps, budget limits (representing cost in tokens or compute), and explicit approval gates for sensitive operations.

This policy is the cornerstone of our agent's safe operation. Without it, an autonomous agent could easily spiral out of control, incurring excessive costs or performing unauthorized actions. For instance, we'll ensure the Market Data Analyst Agent cannot access the `System_Config_Change` tool, and any `Portfolio_Update` action requires explicit human approval due to its `critical` risk class.

The policy can be thought of as a function that evaluates an agent's proposed action in its current state to make a decision:

$$\text{Policy Function} P(action, state) \rightarrow \text{Decision} \in \{\text{Approved, Denied, Approval Required}\}$$

where the decision is based on conditions like tool permission, step limit, budget limit, and approval gate checks.

The decision is based on a set of logical conditions:
*   **Tool Permission Check:** Is $T_{\text{proposed}} \in T_{\text{allowed}}$? (Is the proposed tool in the list of tools the agent is allowed to use?)
*   **Step Limit Check:** Is $S_{\text{current}} < S_{\text{max}}$? (Is the current step count less than the maximum allowed steps?)
*   **Budget Limit Check:** Is $C_{\text{action}} + C_{\text{current}} \leq C_{\text{max}}$? (Will the cost of the proposed action plus the current incurred cost stay within the maximum budget?)
*   **Approval Gate Check:** Is $R(T_{\text{proposed}}) \geq R_{\text{threshold}}$ or $A(T_{\text{proposed}}) \in A_{\text{approval\_required}}$? (Does the proposed tool's risk class or access level require explicit human approval?)

If any of these conditions are not met, a violation or approval requirement is triggered.

**How to Use:**
1.  Navigate to the "Policy Editor" page.
2.  You will see various configuration options for the agent's policy:
    *   **Allowed Tools:** Select which of the tools from your registry the agent is explicitly allowed to use. You can select multiple tools.
    *   **Max Steps Per Run:** Set the maximum number of actions the agent can take within a single task run. Exceeding this triggers a violation.
    *   **Budget Limit:** Define a maximum cost (e.g., token count, computational cost proxy) the agent can incur during a task run. Exceeding this triggers a violation.
    *   **Approval Required for Access Levels:** Choose which access levels (e.g., 'write', 'execute') automatically trigger an `APPROVAL_REQUIRED` state if a tool with that access level is used.
    *   **Approval Required for Risk Classes:** Select which risk classes (e.g., 'high', 'critical') automatically trigger an `APPROVAL_REQUIRED` state.
    *   **Escalation Rule:** Define a message or action to be taken if a severe policy violation occurs.
3.  Adjust the values as needed.
4.  Click "Update Agent Policy" to save your changes to the application's session state.

## 4. Designing Test Scenarios: Defining Agent Tasks
Duration: 00:07:00

With our tools and policies in place, the next crucial step is to define specific tasks for our agent to perform in the simulation. These tasks are not just random assignments; they are carefully crafted test cases designed to validate our policies under different conditions. As a Platform Engineer, I need to ensure these tasks will trigger:
1.  A standard, compliant execution.
2.  A policy violation (e.g., attempting a disallowed tool or exceeding limits).
3.  A scenario requiring explicit human approval.

This strategic task definition is key to thoroughly stress-testing our guardrails.

**How to Use:**
1.  Navigate to the "Task Runner" page.
2.  You will see a data editor for "Current Task Definitions". Each task has:
    *   `task_id`: A unique identifier for the task.
    *   `task_description`: A human-readable description of what the agent should achieve.
    *   `expected_actions`: A JSON array representing the sequence of actions the agent is *expected* to take to complete the task. This includes the `tool_name` and `params` (parameters for the mock function), and an estimated `cost` for the action. This is crucial for policy evaluation.
        *   Example: `[{"tool_name": "MarketDataAPI_Read", "params": {"query": "tech stock trends"}, "cost": 10}]`
    *   `expected_outcome`: A description of what the ideal result of the task should be.
3.  **To Add a Task:** Click `+ Add row` at the bottom of the table and fill in the task details. Ensure `expected_actions` is valid JSON.
4.  **To Edit a Task:** Click any cell to modify its content.
5.  **To Delete a Task:** Hover over a row and click the trash can icon.
6.  Click "Update Task Definitions" to save your changes.

**Running the Simulation:**
1.  After defining or updating your tasks, locate the "Run Agent Simulation" button.
2.  Click this button to start the simulation. The application will use the currently defined Tool Registry, Agent Policy, and Task Definitions to simulate the agent's behavior.
3.  A spinner will indicate that the simulation is running.
4.  Upon completion, a success message will appear, and you will be automatically navigated to the "Simulation & Results" page to review the findings.

<aside class="negative">
<b>Warning:</b> Ensure your Tool Registry, Agent Policy, and Task Definitions are loaded and configured before running the simulation. If any are empty, the simulation cannot proceed, and an error message will be displayed.
</aside>

## 5. The Policy Enforcer: Implementing the Agent State Machine & Policy Engine
Duration: 00:08:00

This is the engineering core of our validation. As a Platform Engineer, I need to implement a robust `AgentSimulator` that models the agent's behavior as a deterministic state machine. Crucially, before *each* simulated action, a `PolicyEngine` must intercede to check for violations against our defined `agent_policy.json` and `tool_registry.json`.

The agent will transition through states like `INIT`, `PLAN`, `ACT`, `REVIEW`, `APPROVAL_REQUIRED`, `COMPLETE`, or `VIOLATION`. This state machine ensures every decision and its outcome is traceable.

The simulation process is governed by a state transition function:

$$\text{State Transition Function} \delta(S_t, A_t, P_{\text{outcome}})$$

where $S_t$ is the current state, $A_t$ is the proposed action, and $P_{\text{outcome}}$ is the policy engine's decision.

For each step $t$:
1.  Agent proposes action $A_t$.
2.  Policy Engine evaluates $P(A_t, S_t) \rightarrow P_{\text{outcome}}$.
3.  New state $S_{\text{t+1}} = \delta(S_t, A_t, P_{\text{outcome}})$.

Example transitions:
*   If $P_{\text{outcome}} = \text{APPROVED}$, then $S_{\text{t+1}} = \text{ACT}$.
*   If $P_{\text{outcome}} = \text{REQUIRES\_APPROVAL}$, then $S_{\text{t+1}} = \text{APPROVAL\_REQUIRED}$.
*   If $P_{\text{outcome}} = \text{DENIED\_VIOLATION}$, then $S_{\text{t+1}} = \text{VIOLATION}$.

The `PolicyEngine` also tracks resource consumption (steps, budget). For budget, if $C_{\text{action}}$ is the cost of the proposed action and $B_{\text{current}}$ is the remaining budget, the new budget $B_{\text{next}} = B_{\text{current}} - C_{\text{action}}$. A violation occurs if $B_{\text{next}} < 0$. Similarly for steps, if $S_{\text{current}}$ is the current step count and $S_{\text{max}}$ is the maximum, a violation occurs if $S_{\text{current}} + 1 > S_{\text{max}}$.

## 6. Auditing Agent Behavior: Analyzing Violations and Generating Reports
Duration: 00:07:00

The simulation generated a wealth of data about the agent's behavior. My job as a Platform Engineer doesn't end with running the simulation; I must analyze the results, particularly the `violations_summary.json` and `execution_trace.json`, to confirm that policies were correctly enforced.

This step involves reviewing the audit logs to confirm that:
1.  Compliant actions proceeded without hindrance.
2.  Disallowed tool usage was correctly identified and stopped.
3.  Budget and step limits were enforced.
4.  Sensitive operations correctly triggered an `APPROVAL_REQUIRED` state.

Finally, I will generate a comprehensive `session09_executive_summary.md` report and an `evidence_manifest.json` (with SHA-256 hashes for integrity), providing concrete proof to stakeholders that the agent is ready for deployment. This output is our deliverable, ensuring auditability and confidence in the agent's safety.

**How to Use:**
1.  After running a simulation from the "Task Runner" page, you will automatically be directed to the "Simulation & Results" page.
2.  **Execution Trace:** This table provides a detailed, step-by-step log of every action the agent attempted, the policy engine's decision, the resulting state, and any associated costs or violations. Review this to understand the agent's behavior path for each task.
3.  **Violation Summary:** This table summarizes any policy violations or approval requirements that occurred during the simulation across all tasks. This is a quick way to identify if any of your guardrails were triggered.
4.  Analyze the data:
    *   Look for `VIOLATION` states in the execution trace. Do they correspond to the expected policy breaches you designed tasks for?
    *   Check for `APPROVAL_REQUIRED` states. Did sensitive actions correctly flag for human intervention?
    *   Verify that tasks designed to be compliant proceeded to `COMPLETE` without unexpected interruptions.
    *   Examine the `violations_summary` for a high-level overview of all triggered policy conditions.

## 7. Output Artifacts and Evidence Manifest
Duration: 00:05:00

All generated output artifacts from a simulation run are stored in a run-specific directory within `reports/session09/`.

The following artifacts are produced for each simulation run:
*   `tool_registry.json`: A snapshot of the tool registry used for the simulation.
*   `agent_policy.json`: A snapshot of the agent policy applied during the simulation.
*   `execution_trace.json`: A detailed log of every step, policy decision, and state transition.
*   `violations_summary.json`: A summary of all policy violations and approval requirements.
*   `session09_executive_summary.md`: A markdown report summarizing the simulation findings.
*   `config_snapshot.json`: A snapshot of the overall application configuration at the time of the run.
*   `evidence_manifest.json`: A manifest listing all generated artifacts along with their SHA-256 hashes for integrity verification.

All artifacts within the evidence manifest are hashed with SHA-256 to ensure data integrity and auditability. This provides immutable proof that the simulation results have not been tampered with, which is critical for compliance and trust.

**How to Use:**
1.  Navigate to the "Export Panel" page.
2.  If a simulation has been run, you will see details about the "Last Simulation Output" including the Run ID and the directory where artifacts are located.
3.  You will be provided with options to:
    *   **Download All Artifacts as .zip:** Click the provided link or button to download a compressed archive containing all the artifacts from the last simulation run. This is useful for offline review and archival.
    *   **View Executive Summary:** The content of the `session09_executive_summary.md` will be displayed directly in the app.
    *   **View Evidence Manifest:** The content of the `evidence_manifest.json` will be displayed directly in the app, showing the names and SHA-256 hashes of all generated files.

<aside class="positive">
<b>Best Practice:</b> Always download the zip file and review the `evidence_manifest.json` to ensure the integrity and completeness of your audit trail. This is your proof of compliance!
</aside>
