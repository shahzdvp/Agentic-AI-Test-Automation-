import time

from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from loguru import logger

from ai_testgen.generator.base import BaseTestGenerator
from ai_testgen.schemas import GeneratedTestSuite


class LangChainTestGenerator(BaseTestGenerator):
    """Test generator using LangChain and Google's Generative AI."""

    def __init__(self, model_name: str, api_key: str, temperature: float = 0.1):
        self.model_name = model_name
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=temperature
        )
        self.structured_llm = self.llm.with_structured_output(GeneratedTestSuite)

        self.system_prompt = (
            "You are an expert Python QA engineer specializing in pytest. "
            "Your task is to generate a comprehensive test suite for the provided Python source code. "
            "Follow these guidelines:\n"
            "- Generate happy path, edge cases, and exception handling tests.\n"
            "- Use pytest conventions (e.g., fixtures, parametrize, markers).\n"
            "- Return complete, executable pytest code in the requested structured format.\n"
            "- Ensure the test function names are descriptive.\n"
            "- CRITICAL: The absolute module path is provided at the top of the source code as a comment. You MUST use this path in your import statements (e.g. `from examples.calculator import ...`). Do not use relative imports.\n"
            "- CRITICAL: When writing multi-line code for fixtures or test cases, use ACTUAL newlines. Do NOT use escaped literal `\\n` characters in the string.\n"
        )

        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", "Source Code:\n{source_code}\n\nFeedback/Errors:\n{feedback}\n\nPlease generate the test suite.")
        ])

        self.chain = self.prompt_template | self.structured_llm

    def generate(self, source_code: str, feedback: str | None = None) -> GeneratedTestSuite:
        """Generate tests for source code, optionally incorporating feedback."""
        feedback_str = feedback if feedback else "None"
        logger.info(f"Generating tests for source code (length: {len(source_code)} chars) with model {self.model_name}")

        start_time = time.time()
        try:
            result = self.chain.invoke({
                "source_code": source_code,
                "feedback": feedback_str
            })
            duration = time.time() - start_time
            logger.info(f"Generation completed in {duration:.2f} seconds.")
            return result
        except Exception as e:
            logger.error(f"API error during generation: {e}")
            raise
