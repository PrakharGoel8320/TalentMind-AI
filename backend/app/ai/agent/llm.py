import os
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_ollama import ChatOllama
try:
    from langchain_openai import ChatOpenAI
except ImportError:
    ChatOpenAI = None

class FakeChatModel(BaseChatModel):
    """A fake chat model for testing purposes."""
    @property
    def _llm_type(self) -> str:
        return "fake-chat-model"
        
    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        from langchain_core.messages import AIMessage
        from langchain_core.outputs import ChatResult, ChatGeneration
        msg = AIMessage(content="I have processed your request.")
        return ChatResult(generations=[ChatGeneration(message=msg)])
        
    def bind_tools(self, tools, **kwargs):
        return self

def get_llm() -> BaseChatModel:
    """
    Factory to return the appropriate LLM based on environment variables.
    Defaults to FakeChatModel if no provider is configured, to ensure offline tests pass.
    """
    provider = os.getenv("LLM_PROVIDER", "mock").lower()
    
    if provider == "openai":
        if ChatOpenAI is None:
            raise ImportError("langchain-openai is not installed")
        return ChatOpenAI(model=os.getenv("LLM_MODEL", "gpt-4o"), temperature=0)
    elif provider == "ollama":
        return ChatOllama(model=os.getenv("LLM_MODEL", "llama3"), temperature=0)
    else:
        # Default to a mock for safe testing without keys
        return FakeChatModel()
