
import pytest
from streamlit.testing.v1 import AppTest
import json
import os
import shutil
import base64
from unittest.mock import patch, MagicMock

# --- Global Paths for Mocking ---
# These paths are assumed to be used by source.py and app.py
# In a real test, these might be handled by a pytest fixture and temporary directories.
# For this exercise, we'll use fixed paths and clean them up.
tool_registry_path = "temp_tool_registry.json"
agent_policy_path = "temp_agent_policy.json"
task_definitions_path = "temp_task_definitions.json"
output_dir_base = "reports/session09/"
mock_run_id = "test_run_123"
mock_current_run_output_dir = os.path.join(output_dir_base, mock_run_id)

# --- Dummy Data for Mocking ---
sample_tool_registry = [
    {"tool_name": "MarketDataAPI_Read", "description": "Read market data", "access_level": "read-only", "risk_class": "low", "mock_function_name": "mock_read_market_data"},
    {"tool_name": "Portfolio_Update", "description": "Update portfolio", "access_level": "write", "risk_class": "critical", "mock_function_name": "mock_update_portfolio"}
]

sample_agent_policy = {
    "allowed_tools": ["MarketDataAPI_Read"],
    "max_steps_per_run": 5,
    "budget_limit": 100,
    "approval_required_for": {"access_levels": ["write"], "risk_classes": ["critical"]},
    "escalation_rule": "Notify Security Team and Terminate Agent"
}

sample_task_definitions = [
    {"task_id": "task_1", "task_description": "Read market data", "expected_actions": [{"tool_name": "MarketDataAPI_Read", "params": {"query": "tech stock trends"}, "cost": 10}], "expected_outcome": "Success"},
    {"task_id": "task_2", "task_description": "Update portfolio (should require approval)", "expected_actions": [{"tool_name": "Portfolio_Update", "params": {"symbol": "ABC", "quantity": 100}, "cost": 50}], "expected_outcome": "Approval Required"}
]

mock_execution_trace = [
    {"task_id": "task_1", "step": 1, "action": "tool_call", "tool_name": "MarketDataAPI_Read", "status": "APPROVED", "cost": 10, "state": "ACT"},
    {"task_id": "task_1", "step": 2, "action": "return_result", "status": "COMPLETE", "state": "COMPLETE"}
]
mock_violations_summary = [
    {"task_id": "task_2", "violation_type": "APPROVAL_REQUIRED", "details": "Action 'Portfolio_Update' requires approval due to critical risk class.", "step": 1}
]

# --- Helper Functions for File System Cleanup/Setup ---
def _create_dummy_artifact_files():
    """Creates dummy files within the mock output directory to simulate simulator output."""
    os.makedirs(mock_current_run_output_dir, exist_ok=True)
    with open(os.path.join(mock_current_run_output_dir, "execution_trace.json"), 'w') as f:
        json.dump(mock_execution_trace, f)
    with open(os.path.join(mock_current_run_output_dir, "violations_summary.json"), 'w') as f:
        json.dump(mock_violations_summary, f)
    with open(os.path.join(mock_current_run_output_dir, "session09_executive_summary.md"), 'w') as f:
        f.write("# Executive Summary Test\nThis is a test summary.")
    with open(os.path.join(mock_current_run_output_dir, "evidence_manifest.json"), 'w') as f:
        json.dump({"files": [{"name": "test.txt", "hash": "abc"}]}, f)

def _cleanup_temp_dirs():
    """Removes any temporary directories and files created by tests/mocks."""
    if os.path.exists(tool_registry_path):
        os.remove(tool_registry_path)
    if os.path.exists(agent_policy_path):
        os.remove(agent_policy_path)
    if os.path.exists(task_definitions_path):
        os.remove(task_definitions_path)
    if os.path.exists(output_dir_base):
        shutil.rmtree(output_dir_base, ignore_errors=True)

# --- Mock Classes/Functions for `source.py` ---

# Mock for AgentSimulator class
class MockAgentSimulator:
    def __init__(self, tool_registry, agent_policy, task_definitions):
        self.tool_registry = tool_registry
        self.agent_policy = agent_policy
        self.task_definitions = task_definitions
        self.execution_trace = []
        self.violations_summary = []
        self.run_id = mock_run_id
        self.current_run_output_dir = mock_current_run_output_dir

    def run_all_tasks(self):
        # Simulate running tasks and populating results
        self.execution_trace = mock_execution_trace
        self.violations_summary = mock_violations_summary
        _create_dummy_artifact_files() # Create files so app.py can find them later

    def save_artifacts(self):
        # Simulate saving artifacts
        pass

# Mock for create_tool_registry, create_agent_policy, create_task_definitions
# These functions from source.py just create the files. We don't need them to actually write for testing the app's UI.
# They are called, but their effect on the filesystem will be ignored/overridden by our mock_open.
def mock_create_tool_registry(path): pass
def mock_create_agent_policy(path): pass
def mock_create_task_definitions(path): pass

# --- Test Functions ---

@pytest.fixture(autouse=True)
def run_around_tests():
    _cleanup_temp_dirs()
    yield
    _cleanup_temp_dirs()

def test_initial_state_and_overview_page():
    at = AppTest.from_file("app.py").run()

    # Verify session state initialization
    assert at.session_state['openai_api_key'] == ''
    assert at.session_state['tool_registry'] == []
    assert at.session_state['agent_policy'] == {}
    assert at.session_state['task_definitions'] == []
    assert at.session_state['execution_trace'] == []
    assert at.session_state['violations_summary'] == []
    assert at.session_state['run_id'] is None
    assert at.session_state['current_run_output_dir'] is None
    assert at.session_state['page'] == 'Overview'

    # Verify main title
    assert at.title[0].value == "QuLab: Lab 9: Agent Runtime Constraint Simulator"

    # Verify overview page content
    assert at.markdown[0].value.startswith("# Lab 9: Agent Policy Sandbox & Guardrail Validation")
    assert "Welcome, fellow Platform Engineer!" in at.markdown[1].value


def test_openai_api_key_input():
    at = AppTest.from_file("app.py").run()

    at.text_input[0].set_value("sk-test-key").run()
    assert at.session_state['openai_api_key'] == "sk-test-key"


def test_sidebar_navigation():
    at = AppTest.from_file("app.py").run()

    # Test navigation to "Tool Registry Editor"
    at.selectbox[0].set_value("Tool Registry Editor").run()
    assert at.session_state['page'] == "Tool Registry Editor"
    assert at.markdown[0].value.startswith("# 3. Building the Agent's Arsenal: Defining the Tool Registry")

    # Test navigation to "Policy Editor"
    at.selectbox[0].set_value("Policy Editor").run()
    assert at.session_state['page'] == "Policy Editor"
    assert at.markdown[0].value.startswith("# 4. Laying Down the Law: Crafting Agent Execution Policies")


@patch('source.create_tool_registry', side_effect=mock_create_tool_registry)
@patch('source.create_agent_policy', side_effect=mock_create_agent_policy)
@patch('source.create_task_definitions', side_effect=mock_create_task_definitions)
@patch('os.path.exists', side_effect=lambda x: x in [tool_registry_path, agent_policy_path, task_definitions_path])
@patch('builtins.open', new_callable=MagicMock)
def test_initialize_reset_sample_data(mock_open, mock_exists, mock_create_tasks, mock_create_policy, mock_create_tools):
    # Configure mock_open to return dummy JSON content when reading
    def mock_open_side_effect(file_path, mode='r', **kwargs):
        if mode == 'r':
            if file_path == tool_registry_path:
                return MagicMock(spec=open, read=lambda: json.dumps(sample_tool_registry))
            elif file_path == agent_policy_path:
                return MagicMock(spec=open, read=lambda: json.dumps(sample_agent_policy))
            elif file_path == task_definitions_path:
                return MagicMock(spec=open, read=lambda: json.dumps(sample_task_definitions))
        return MagicMock(spec=open)

    mock_open.side_effect = mock_open_side_effect

    at = AppTest.from_file("app.py").run()

    # Click the "Initialize/Reset Sample Data" button
    at.button[0].click().run()

    # Verify session state is populated with sample data
    assert at.session_state['tool_registry'] == sample_tool_registry
    assert at.session_state['agent_policy'] == sample_agent_policy
    assert at.session_state['task_definitions'] == sample_task_definitions
    assert at.success[0].value == "Sample data initialized!"
    assert at.session_state['page'] == 'Overview'


def test_tool_registry_editor_page_interactions():
    at = AppTest.from_file("app.py").run()

    at.session_state['tool_registry'] = sample_tool_registry
    at.session_state['page'] = 'Tool Registry Editor'
    at.run()

    assert at.data_editor[0].value == sample_tool_registry

    edited_registry = [
        {"tool_name": "MarketDataAPI_Read", "description": "Read market data updated", "access_level": "read-only", "risk_class": "low", "mock_function_name": "mock_read_market_data"},
        {"tool_name": "Portfolio_Update", "description": "Update portfolio", "access_level": "write", "risk_class": "critical", "mock_function_name": "mock_update_portfolio"}
    ]
    at.data_editor[0].set_value(edited_registry).run()
    at.button[0].click().run()
    assert at.session_state['tool_registry'] == edited_registry
    assert at.success[0].value == "Tool registry updated in session state!"


def test_policy_editor_page_interactions():
    at = AppTest.from_file("app.py").run()

    at.session_state['tool_registry'] = sample_tool_registry # For multiselect options
    at.session_state['agent_policy'] = sample_agent_policy
    at.session_state['page'] = 'Policy Editor'
    at.run()

    assert at.multiselect[0].value == sample_agent_policy['allowed_tools']
    assert at.number_input[0].value == sample_agent_policy['max_steps_per_run']

    at.multiselect[0].set_value(["MarketDataAPI_Read", "Portfolio_Update"]).run()
    at.number_input[0].set_value(10).run()
    at.button[0].click().run() # This button updates the policy

    expected_policy = {**sample_agent_policy, "allowed_tools": ["MarketDataAPI_Read", "Portfolio_Update"], "max_steps_per_run": 10}
    assert at.session_state['agent_policy'] == expected_policy
    assert at.success[0].value == "Agent policy updated in session state!"


def test_task_runner_page_interactions():
    at = AppTest.from_file("app.py").run()

    at.session_state['task_definitions'] = sample_task_definitions
    at.session_state['page'] = 'Task Runner'
    at.run()

    assert at.data_editor[0].value == sample_task_definitions

    edited_tasks = [
        {"task_id": "task_1", "task_description": "Read market data updated", "expected_actions": [{"tool_name": "MarketDataAPI_Read", "params": {"query": "tech stock trends"}, "cost": 10}], "expected_outcome": "Success"},
    ]
    at.data_editor[0].set_value(edited_tasks).run()
    at.button[0].click().run()
    assert at.session_state['task_definitions'] == edited_tasks
    assert at.success[0].value == "Task definitions updated in session state!"


@patch('source.create_tool_registry', side_effect=mock_create_tool_registry)
@patch('source.AgentSimulator', new=MockAgentSimulator)
def test_run_agent_simulation_success(mock_create_tools):
    at = AppTest.from_file("app.py").run()

    at.session_state['tool_registry'] = sample_tool_registry
    at.session_state['agent_policy'] = sample_agent_policy
    at.session_state['task_definitions'] = sample_task_definitions
    at.session_state['page'] = 'Task Runner'
    at.run()

    # The "Run Agent Simulation" button is the second button on the page.
    at.button[1].click().run()

    assert at.session_state['execution_trace'] == mock_execution_trace
    assert at.session_state['violations_summary'] == mock_violations_summary
    assert at.session_state['run_id'] == mock_run_id
    assert at.session_state['current_run_output_dir'] == mock_current_run_output_dir
    assert at.success[0].value == f"Simulation complete! Run ID: `{mock_run_id}`. Navigate to 'Simulation & Results' to view findings."
    assert at.session_state['page'] == 'Simulation & Results'


def test_run_agent_simulation_missing_data():
    at = AppTest.from_file("app.py").run()

    at.session_state['page'] = 'Task Runner'
    at.run()

    # Ensure data is truly empty for this test
    at.session_state['tool_registry'] = []
    at.session_state['agent_policy'] = {}
    at.session_state['task_definitions'] = []
    at.run() # Re-render to ensure conditions are met for error message

    # The "Run Agent Simulation" button
    at.button[1].click().run()

    assert at.error[0].value == "Please ensure Tool Registry, Agent Policy, and Task Definitions are loaded/configured before running."
    assert at.session_state['execution_trace'] == []
    assert at.session_state['violations_summary'] == []


def test_simulation_results_page_content():
    at = AppTest.from_file("app.py").run()

    at.session_state['execution_trace'] = mock_execution_trace
    at.session_state['violations_summary'] = mock_violations_summary
    at.session_state['run_id'] = mock_run_id
    at.session_state['current_run_output_dir'] = mock_current_run_output_dir
    at.session_state['page'] = 'Simulation & Results'
    at.run()

    assert at.markdown[6].value == f"### Simulation Results for Run ID: `{mock_run_id}`"
    assert at.dataframe[0].value.to_dict('records') == mock_execution_trace
    assert at.dataframe[1].value.to_dict('records') == mock_violations_summary


@patch('os.path.exists', side_effect=lambda x: x.startswith(output_dir_base) or x == os.path.join(os.path.dirname(mock_current_run_output_dir), f"Session_09_{mock_run_id}.zip"))
@patch('shutil.make_archive', return_value=os.path.join(os.path.dirname(mock_current_run_output_dir), f"Session_09_{mock_run_id}.zip"))
@patch('builtins.open', new_callable=MagicMock)
def test_export_panel_page_content(mock_open, mock_make_archive, mock_exists):
    # Setup mock_open for reading artifact files
    def mock_open_side_effect(file_path, mode='r', **kwargs):
        if mode == 'rb' and file_path == os.path.join(os.path.dirname(mock_current_run_output_dir), f"Session_09_{mock_run_id}.zip"):
            return MagicMock(spec=open, read=lambda: b"zip_file_content")
        elif mode == 'r':
            if file_path == os.path.join(mock_current_run_output_dir, "session09_executive_summary.md"):
                return MagicMock(spec=open, read=lambda: "# Executive Summary Test\nThis is a test summary.")
            elif file_path == os.path.join(mock_current_run_output_dir, "evidence_manifest.json"):
                return MagicMock(spec=open, read=lambda: json.dumps({"files": [{"name": "test.txt", "hash": "abc"}]}))
        return MagicMock(spec=open)

    mock_open.side_effect = mock_open_side_effect

    at = AppTest.from_file("app.py").run()

    at.session_state['run_id'] = mock_run_id
    at.session_state['current_run_output_dir'] = mock_current_run_output_dir
    at.session_state['page'] = 'Export Panel'
    at.run()

    assert at.markdown[0].value.startswith("# 9. Output Artifacts")
    assert at.markdown[3].value == f"### Last Simulation Output (Run ID: `{mock_run_id}`)"
    assert at.markdown[4].value == f"Artifacts located at: `{mock_current_run_output_dir}`"
    assert at.success[0].value == f"All artifacts for run `{mock_run_id}` bundled and ready for download."

    # Verify content of executive summary and evidence manifest
    assert at.code[0].value == "# Executive Summary Test\nThis is a test summary."
    assert at.json[0].value == {"files": [{"name": "test.txt", "hash": "abc"}]}

    # Verify that make_archive was called
    mock_make_archive.assert_called_once_with(
        os.path.join(os.path.dirname(mock_current_run_output_dir), f"Session_09_{mock_run_id}"),
        'zip',
        mock_current_run_output_dir
    )
