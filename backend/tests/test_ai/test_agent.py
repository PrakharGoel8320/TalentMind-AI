import pytest
import uuid
from typing import Dict, Any, List
from unittest.mock import AsyncMock, patch, MagicMock

from app.ai.agent.state import AgentState
from app.ai.agent.graph import TalentMindAgent
from app.ai.agent.tools import (
    retrieve_candidates_tool,
    analyze_features_tool,
    rank_candidates_tool,
    analyze_behavior_tool,
    finalize_and_fuse_tool
)
from app.api.v1.agent import AgentRequest, AgentResponse
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, ToolCall

# ---------------------------------------------------------
# Test 1: State creation
# ---------------------------------------------------------
def test_state_creation():
    state: AgentState = {
        "job_id": "test_job_1",
        "job_description": "We need a Python developer.",
        "recruiter_request": "Find me python devs.",
        "messages": [],
        "retrieved_candidates": [],
        "analyzed_candidates": [],
        "final_ranking": [],
        "explanation": "Test explanation",
        "status": "processing",
        "errors": []
    }
    assert state["job_id"] == "test_job_1"
    assert state["explanation"] == "Test explanation"

# ---------------------------------------------------------
# Test 2 & 3: Tool Invocation & Chaining (using mocks)
# ---------------------------------------------------------
@patch('app.ai.agent.tools.get_retrieval_service')
@patch('app.ai.agent.tools.get_feature_extractor')
@patch('app.ai.agent.tools.AsyncSessionLocal')
def test_tool_chaining(mock_db, mock_extractor_factory, mock_retrieval_factory):
    # Mock retrieval
    mock_retrieval = MagicMock()
    mock_retrieval.search_candidates.return_value = [{"candidate_id": "cand_1", "score": 0.85}]
    mock_retrieval_factory.return_value = mock_retrieval
    
    # Mock DB Hydration
    class DummyCand:
        def __init__(self):
            self.id = "cand_1"
            self.profile_jsonb = {"skills": ["Python"]}
            
    mock_session = AsyncMock()
    mock_session.__aenter__.return_value = mock_session
    mock_res = MagicMock()
    mock_res.scalars.return_value.all.return_value = [DummyCand()]
    mock_session.execute.return_value = mock_res
    mock_db.return_value = mock_session
    
    # Tool 1: Retrieval
    candidates = retrieve_candidates_tool.invoke({"job_description": "Python dev", "top_k": 5})
    assert len(candidates) == 1
    assert candidates[0]["candidate_id"] == "cand_1"
    
    # Tool 2: Feature Extraction
    mock_extractor = MagicMock()
    mock_extractor.extract_features.return_value = [{"candidate_id": "cand_1", "skill_match_score": 100.0}]
    mock_extractor_factory.return_value = mock_extractor
    
    extracted = analyze_features_tool.invoke({"job_description": "Python dev", "candidates": candidates})
    assert extracted[0]["skill_match_score"] == 100.0

# ---------------------------------------------------------
# Test 4: Decision branching (LLM Mocking)
# ---------------------------------------------------------
def test_decision_branching():
    agent = TalentMindAgent()
    
    # Test path 1: normal tool request
    state = {"messages": [HumanMessage(content="Start")]}
    
    # If the LLM generates a tool call, we should continue
    tool_call = ToolCall(name="retrieve_candidates_tool", args={"job_description": "test", "top_k": 10}, id="123")
    state["messages"].append(AIMessage(content="", tool_calls=[tool_call]))
    
    assert agent._should_continue(state) == "continue"
    
    # Test path 2: End of graph
    state["messages"].append(ToolMessage(content="done", tool_call_id="123", name="retrieve_candidates_tool"))
    state["messages"].append(AIMessage(content="I am finished."))
    
    assert agent._should_continue(state) == "end"

# ---------------------------------------------------------
# Test 5: Deterministic ranking preservation
# ---------------------------------------------------------
@patch('app.ai.agent.tools.get_retrieval_service')
@patch('app.ai.agent.tools.AsyncSessionLocal')
def test_deterministic_ranking(mock_db, mock_retrieval_factory):
    # This proves that identical inputs to tools yield identical outputs
    mock_retrieval = MagicMock()
    mock_retrieval.search_candidates.return_value = [{"candidate_id": "cand_2", "score": 0.9}]
    mock_retrieval_factory.return_value = mock_retrieval
    
    class DummyCand:
        def __init__(self):
            self.id = "cand_2"
            self.profile_jsonb = {"skills": ["Java"]}
            
    mock_session = AsyncMock()
    mock_session.__aenter__.return_value = mock_session
    mock_res = MagicMock()
    mock_res.scalars.return_value.all.return_value = [DummyCand()]
    mock_session.execute.return_value = mock_res
    mock_db.return_value = mock_session
    
    # Run 1
    run1 = retrieve_candidates_tool.invoke({"job_description": "Java dev", "top_k": 5})
    # Run 2
    run2 = retrieve_candidates_tool.invoke({"job_description": "Java dev", "top_k": 5})
    
    assert run1 == run2

# ---------------------------------------------------------
# Test 6: Tool failure graceful handling
# ---------------------------------------------------------
@patch('app.ai.agent.tools.get_retrieval_service')
def test_tool_failure_handling(mock_retrieval_factory):
    mock_retrieval = MagicMock()
    mock_retrieval.search_candidates.side_effect = Exception("FAISS crashed")
    mock_retrieval_factory.return_value = mock_retrieval
    
    try:
        retrieve_candidates_tool.invoke({"job_description": "test", "top_k": 5})
        assert False, "Should have thrown"
    except Exception as e:
        assert str(e) == "FAISS crashed"
    # The LangGraph ToolNode natively traps tool errors and returns ToolMessage with error
    
# ---------------------------------------------------------
# Test 7: LLM Unavailable
# ---------------------------------------------------------
def test_llm_unavailable():
    agent = TalentMindAgent()
    # Replace LLM with one that raises Exception
    agent.llm_with_tools = MagicMock()
    agent.llm_with_tools.invoke.side_effect = Exception("OpenAI API Down")
    
    state = {"messages": [HumanMessage(content="Hello")]}
    result = agent._call_agent(state)
    
    assert "errors" in result
    assert result["errors"] == ["OpenAI API Down"]
    assert result["status"] == "error"
    assert "Error interacting with LLM" in result["messages"][0].content

# ---------------------------------------------------------
# Test 8: Maximum iteration protection
# ---------------------------------------------------------
def test_maximum_iteration_protection():
    agent = TalentMindAgent()
    
    # Create a mock LLM that ALWAYS requests a tool, creating an infinite loop
    mock_llm = MagicMock()
    tool_call = ToolCall(name="fake_tool", args={}, id="1")
    mock_llm.invoke.return_value = AIMessage(content="", tool_calls=[tool_call])
    agent.llm_with_tools = mock_llm
    
    # Tool node must return something
    agent.graph = agent.graph  # just referring to it
    
    # If we run it with recursion_limit=2, it should raise GraphRecursionError
    from langgraph.errors import GraphRecursionError
    
    with pytest.raises(GraphRecursionError):
        initial_state = {
            "job_id": "test", "job_description": "test", "recruiter_request": "test",
            "messages": [HumanMessage(content="test")],
            "status": "processing", "errors": []
        }
        agent.graph.invoke(initial_state, {"recursion_limit": 2})

# ---------------------------------------------------------
# Test 9: Structured output
# ---------------------------------------------------------
def test_structured_output():
    import os
    with patch.dict(os.environ, {"LLM_PROVIDER": "langgraph"}):
        agent = TalentMindAgent()
        agent.graph = MagicMock()
        
        # Mock the final state returned by LangGraph
        agent.graph.invoke.return_value = {
            "job_id": "job_1",
            "status": "completed",
            "errors": [],
            "messages": [
                ToolMessage(content='[{"candidate_id": "1", "final_score": 90.0}]', name="finalize_and_fuse_tool", tool_call_id="1"),
                AIMessage(content="Here are the top candidates.")
            ]
        }
        
        result = agent.run("job_1", "JD", "Request")
    
    assert result["job_id"] == "job_1"
    assert result["status"] == "completed"
    assert result["explanation"] == "Here are the top candidates."
    assert len(result["candidates"]) == 1
    assert result["candidates"][0]["candidate_id"] == "1"

