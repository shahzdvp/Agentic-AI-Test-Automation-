from ai_testgen.config import Settings
from ai_testgen.generator.langchain_gen import LangChainTestGenerator
from ai_testgen.orchestrator.pipeline import FrameworkOrchestrator
from ai_testgen.parser.ast_parser import PythonASTParser
from ai_testgen.runner.pytest_runner import PytestRunner

def create_orchestrator(settings: Settings) -> FrameworkOrchestrator:
    """Factory function to construct the fully injected test orchestrator."""
    parser = PythonASTParser()
    
    # In the future, we can check settings.llm_provider to swap LangChainTestGenerator 
    # for an OpenAITestGenerator or AnthropicTestGenerator here without breaking the CLI.
    generator = LangChainTestGenerator(
        model_name=settings.model_name,
        api_key=settings.google_api_key.get_secret_value(),
        temperature=settings.temperature
    )
    
    runner = PytestRunner()
    
    return FrameworkOrchestrator(
        parser=parser,
        generator=generator,
        runner=runner,
        max_retries=settings.max_retries
    )
