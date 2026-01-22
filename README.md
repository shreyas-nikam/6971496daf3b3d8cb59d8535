Here's a comprehensive `README.md` file for your Streamlit application lab project.

---

# QuLab: Lab 9: Agent Runtime Constraint Simulator

## Agent Policy Sandbox & Guardrail Validation

![QuantUniversity Logo](https://www.quantuniversity.com/assets/img/logo5.jpg)

### A Platform Engineer's Workflow for AI Agent Pre-Deployment Validation

This project presents **QuLab: Lab 9: Agent Runtime Constraint Simulator**, a Streamlit application designed to simulate and validate the operational policies and guardrails for autonomous AI agents. Developed from the perspective of a Platform Engineer, this tool addresses the critical need to ensure that AI agents operate within strict corporate governance, security, and financial controls before deployment into production environments.

The application provides a simulated environment where users can define an agent's available tools, configure its operational policies (e.g., budget limits, approval gates), simulate various tasks, and meticulously audit its behavior. The core objective is to generate auditable evidence that an AI agent is safe, compliant, and ready for enterprise-grade deployment, focusing on traceability and policy enforcement at every step.

---

## Table of Contents

1.  [Features](#features)
2.  [Getting Started](#getting-started)
    *   [Prerequisites](#prerequisites)
    *   [Installation](#installation)
3.  [Usage](#usage)
4.  [Project Structure](#project-structure)
5.  [Core Concepts & Technology Stack](#core-concepts--technology-stack)
6.  [Contributing](#contributing)
7.  [License](#license)
8.  [Contact](#contact)

---

## 1. Features

The **QuLab: Lab 9** application guides users through a structured workflow for AI agent validation, offering the following key functionalities:

*   **Interactive Overview**: An introductory section explaining the purpose and positioning of the lab, setting the context for AI agent risk control and auditability.
*   **Tool Registry Editor**:
    *   Define and manage the agent's available tools.
    *   Specify tool attributes such as `tool_name`, `description`, `access_level` (read-only, write, execute), `risk_class` (low, medium, high, critical), and a `mock_function_name` for simulation.
    *   Establishes the base capabilities and inherent risks of functions the agent might invoke.
*   **Policy Editor**:
    *   Configure strict runtime policies for the agent.
    *   Set `allowed_tools`, `max_steps_per_run`, and `budget_limit` (as a cost proxy).
    *   Define `approval_required_for` specific `access_levels` or `risk_classes`.
    *   Specify an `escalation_rule` for policy violations.
    *   This component serves as the cornerstone for enforcing critical guardrails.
*   **Task Runner**:
    *   Design and define specific `task_definitions` for the agent to perform during simulation.
    *   Tasks include `task_id`, `task_description`, `expected_actions` (JSON array), and `expected_outcome`.
    *   Tasks are crafted to test compliant execution, trigger policy violations, and simulate scenarios requiring human approval.
    *   Initiate the agent simulation process.
*   **Simulation & Results**:
    *   Visualize the agent's `execution_trace` as a detailed log of every step, proposed action, policy decision, and state transition.
    *   Review a `violations_summary` that highlights any policy breaches or approval requirements encountered during the simulation.
    *   This section details the underlying `AgentSimulator` (modeled as a state machine) and `PolicyEngine`, which intercedes before each action to enforce rules.
*   **Export Panel**:
    *   Access and download all generated output artifacts for a specific simulation run as a single `.zip` file.
    *   Artifacts include `tool_registry.json`, `agent_policy.json`, `execution_trace.json`, `violations_summary.json`, `session09_executive_summary.md`, `config_snapshot.json`, and `evidence_manifest.json`.
    *   The `evidence_manifest.json` includes SHA-256 hashes for all artifacts to ensure data integrity and auditability.
    *   Directly view the content of the `session09_executive_summary.md` and `evidence_manifest.json` within the app.
*   **Data Management**:
    *   One-click initialization/reset of sample data for tools, policies, and tasks, enabling quick setup and experimentation.
    *   The application persists configurations in JSON files and session state.

---

## 2. Getting Started

Follow these instructions to set up and run the Streamlit application on your local machine.

### Prerequisites

*   Python 3.8+
*   `pip` (Python package installer)

### Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/your-username/qualtab-lab9-agent-simulator.git
    cd qualtab-lab9-agent-simulator
    ```
    *(Note: Replace `your-username/qualtab-lab9-agent-simulator` with the actual repository path if it exists.)*

2.  **Create a virtual environment** (recommended):
    ```bash
    python -m venv venv
    ```

3.  **Activate the virtual environment**:
    *   On macOS/Linux:
        ```bash
        source venv/bin/activate
        ```
    *   On Windows:
        ```bash
        .\venv\Scripts\activate
        ```

4.  **Install dependencies**:
    Create a `requirements.txt` file in the project root with the following content:
    ```
    streamlit>=1.0.0
    # Add other dependencies if your 'source.py' or future enhancements require them,
    # e.g., openai if the OpenAI API key integration becomes active.
    ```
    Then, install:
    ```bash
    pip install -r requirements.txt
    ```

---

## 3. Usage

To run the Streamlit application:

1.  **Start the application**:
    Ensure your virtual environment is active and navigate to the project root directory where `app.py` is located.
    ```bash
    streamlit run app.py
    ```
    This command will open the application in your default web browser.

2.  **Navigate the Application**:
    *   Use the **sidebar** on the left to navigate between different sections: "Overview", "Tool Registry Editor", "Policy Editor", "Task Runner", "Simulation & Results", and "Export Panel".
    *   **OpenAI API Key**: Optionally, you can input your OpenAI API key in the sidebar. While not fully leveraged in the provided code snippet, this field is available for potential future integrations with LLM-powered agents.
    *   **Initialize/Reset Sample Data**: It's highly recommended to click the "Initialize/Reset Sample Data" button in the sidebar when you first start the application or wish to revert to default configurations. This populates the tool registry, agent policy, and task definitions with example data.

3.  **Follow the Workflow**:
    *   **Tool Registry Editor**: Define or modify the agent's available tools.
    *   **Policy Editor**: Configure the agent's runtime policies, including allowed tools, budget, steps, and approval requirements.
    *   **Task Runner**: Define the simulation scenarios. Once satisfied, click "Run Agent Simulation" to execute the policies against the tasks.
    *   **Simulation & Results**: Review the detailed execution trace and a summary of any policy violations or approval requirements.
    *   **Export Panel**: Download all simulation artifacts, including an executive summary and an evidence manifest for auditability.

---

## 4. Project Structure

The project is organized to separate the Streamlit UI from the core simulation logic and manage data artifacts effectively.

```
qualtab-lab9-agent-simulator/
├── app.py                      # Main Streamlit application file
├── source.py                   # Core simulation logic (AgentSimulator, PolicyEngine, mock tools, data creation)
├── data/                       # Directory for initial/default configuration JSON files
│   ├── tool_registry.json      # Defines available tools for the agent
│   ├── agent_policy.json       # Defines runtime policies and guardrails
│   └── task_definitions.json   # Defines simulation tasks/scenarios
├── reports/                    # Directory for simulation outputs
│   └── session09/              # Root directory for session 09 reports
│       └── <run_id>/           # Unique directory for each simulation run (e.g., 20231027_153045/)
│           ├── tool_registry.json          # Snapshot of tools used in this run
│           ├── agent_policy.json           # Snapshot of policy used in this run
│           ├── task_definitions.json       # Snapshot of tasks used in this run
│           ├── execution_trace.json        # Detailed log of agent's steps and policy decisions
│           ├── violations_summary.json     # Summary of policy violations and approval requirements
│           ├── session09_executive_summary.md # Markdown report summarizing the run
│           ├── config_snapshot.json        # Consolidated snapshot of configurations
│           └── evidence_manifest.json      # List of artifacts with SHA-256 hashes for integrity
├── venv/                       # Python virtual environment (if created)
├── .gitignore                  # Specifies intentionally untracked files to ignore
└── README.md                   # This README file
```

---

## 5. Core Concepts & Technology Stack

This application is built on modern Python frameworks and emphasizes key concepts for secure AI agent deployment:

### Core Concepts

*   **Agent as a Stateful System**: Treats AI agents not merely as prompt loops but as stateful entities with a clear state machine (`INIT`, `PLAN`, `ACT`, `REVIEW`, `APPROVAL_REQUIRED`, `COMPLETE`, `VIOLATION`).
*   **Policy-as-Code**: Defines agent guardrails and constraints explicitly in JSON-based policies (`agent_policy.json`) and a tool registry (`tool_registry.json`).
*   **Policy Engine**: A central component that intercepts every proposed agent action, evaluating it against defined policies before allowing execution.
*   **Auditability**: Generates comprehensive `execution_trace` logs, `violations_summary`, and `evidence_manifest` with SHA-256 hashes to ensure transparent and auditable agent behavior.
*   **Simulation-Driven Validation**: Uses simulated tasks to proactively test policies under various conditions, including expected successes, deliberate violations, and scenarios requiring human oversight.

### Technology Stack

*   **Python**: The primary programming language.
*   **Streamlit**: For building the interactive web-based user interface.
*   **Standard Python Libraries**:
    *   `json`: For handling JSON data for configurations and outputs.
    *   `os`, `shutil`: For file system operations, directory management, and archiving results.
    *   `base64`: For encoding/decoding file data for download.

---

## 6. Contributing

Contributions are welcome! If you have suggestions for improvements, new features, or bug fixes, please feel free to:

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/AmazingFeature`).
3.  Make your changes.
4.  Commit your changes (`git commit -m 'Add some AmazingFeature'`).
5.  Push to the branch (`git push origin feature/AmazingFeature`).
6.  Open a Pull Request.

---

## 7. License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
*(Note: Create a `LICENSE` file in your repository if you want to include it.)*

---

## 8. Contact

For questions, feedback, or collaborations, please contact:

*   **QuantUniversity**
*   **Website**: [https://www.quantuniversity.com](https://www.quantuniversity.com)
*   **Email**: info@quantuniversity.com

---