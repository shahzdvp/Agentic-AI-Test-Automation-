from unittest.mock import MagicMock, patch

import pytest

from ai_testgen.generator.langchain_gen import LangChainTestGenerator
from ai_testgen.schemas import GeneratedTestCase, GeneratedTestSuite


@patch("ai_testgen.generator.langchain_gen.ChatGoogleGenerativeAI")
def test_generator_success(mock_chat_class):
    """Test generating a suite successfully."""
    # Setup mock
    mock_llm = MagicMock()
    mock_structured = MagicMock()

    mock_chat_class.return_value = mock_llm
    mock_llm.with_structured_output.return_value = mock_structured

    # Fake response
    fake_suite = GeneratedTestSuite(
        module_name="test_mod",
        required_imports=["import pytest"],
        fixtures=[],
        test_cases=[
            GeneratedTestCase(
                name="test_foo",
                docstring="test",
                code="def test_foo(): pass",
                is_edge_case=False
            )
        ]
    )

    # We must patch the chain invocation since LangChain creates a pipeline
    with patch("ai_testgen.generator.langchain_gen.ChatPromptTemplate") as mock_template:
        generator = LangChainTestGenerator("gemini-3.6-flash", "fake-key")

        # Override the chain with a simple mock that returns our fake suite
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = fake_suite
        generator.chain = mock_chain

        result = generator.generate("def foo(): pass", feedback=None)

        assert result.module_name == "test_mod"
        assert len(result.test_cases) == 1
        mock_chain.invoke.assert_called_once()
        args = mock_chain.invoke.call_args[0][0]
        assert "def foo(): pass" in args["source_code"]
        assert args["feedback"] == "None"


@patch("ai_testgen.generator.langchain_gen.ChatGoogleGenerativeAI")
def test_generator_api_error(mock_chat_class):
    """Test generator handles API errors by raising."""
    generator = LangChainTestGenerator("gemini-3.6-flash", "fake-key")

    mock_chain = MagicMock()
    mock_chain.invoke.side_effect = Exception("API limit reached")
    generator.chain = mock_chain

    with pytest.raises(Exception, match="API limit reached"):
        generator.generate("def foo(): pass", feedback="Fix it")
