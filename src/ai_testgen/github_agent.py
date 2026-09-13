import os
import sys
import json
import subprocess
from pathlib import Path

from github import Github
from loguru import logger

from ai_testgen.config import get_settings
from ai_testgen.generator.langchain_gen import LangChainTestGenerator
from ai_testgen.orchestrator.pipeline import FrameworkOrchestrator
from ai_testgen.parser.ast_parser import PythonASTParser
from ai_testgen.runner.pytest_runner import PytestRunner


def get_pr_files(gh: Github, repo_name: str, pr_number: int):
    """Fetch the list of modified .py files from the PR."""
    from github import GithubException
    try:
        repo = gh.get_repo(repo_name)
        pr = repo.get_pull(pr_number)
        
        python_files = []
        for file in pr.get_files():
            if file.filename.endswith(".py") and not file.filename.startswith("test_") and not file.filename.startswith("examples/generated"):
                # Only test files that were added or modified (not deleted)
                if file.status in ["added", "modified"]:
                    python_files.append(Path(file.filename))
                    
        return python_files, pr
    except GithubException as e:
        logger.error(f"GitHub API Error: {e.status} - {e.data}")
        if e.status == 403:
            logger.error("Rate limit exceeded or permission denied.")
        return [], None


def commit_and_push(files_added: int):
    """Use system git to commit and push the new tests."""
    if files_added == 0:
        return False
        
    try:
        # Configure git identity for the bot
        subprocess.run(["git", "config", "--local", "user.name", "AI TestGen Bot"], check=True)
        subprocess.run(["git", "config", "--local", "user.email", "bot@ai-testgen.io"], check=True)
        
        # Add generated tests (safe path only)
        subprocess.run(["git", "add", "tests/generated/"], check=True)
        
        # Check if there is anything to commit
        status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        if not status.stdout.strip():
            logger.info("No new test files to commit.")
            return False
            
        subprocess.run(["git", "commit", "-m", "🤖 AI-TestGen: Autonomously generated tests"], check=True)
        subprocess.run(["git", "push"], check=True)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to commit and push: {e}")
        return False


def main():
    logger.info("Booting up AI-TestGen Autonomous Agent...")
    
    # 1. Gather context from GitHub Actions environment
    github_token = os.environ.get("GITHUB_TOKEN")
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    repo_name = os.environ.get("GITHUB_REPOSITORY")
    
    if not all([github_token, event_path, repo_name]):
        logger.error("Missing required GitHub environment variables.")
        sys.exit(1)
        
    # Read the PR event JSON
    with open(event_path, "r") as f:
        event_data = json.load(f)
        
    if "pull_request" not in event_data:
        logger.info("Not a pull request event. Shutting down.")
        sys.exit(0)
        
    pr_number = event_data["pull_request"]["number"]
    
    # 2. Fetch modified files
    gh = Github(github_token)
    files_to_process, pr = get_pr_files(gh, repo_name, pr_number)
    
    if not files_to_process:
        logger.info("No Python files were modified in this PR. Nothing to test.")
        sys.exit(0)
        
    logger.info(f"Found {len(files_to_process)} modified Python files to analyze.")
    
    # 3. Initialize AI TestGen Framework
    settings = get_settings()
    orchestrator = FrameworkOrchestrator(
        parser=PythonASTParser(),
        generator=LangChainTestGenerator(
            model_name=settings.model_name,
            api_key=settings.google_api_key.get_secret_value(),
            temperature=settings.temperature
        ),
        runner=PytestRunner(),
        max_retries=settings.max_retries
    )
    
    # 4. Generate Tests
    total_stats = {"tests_passed": 0, "retries_used": 0}
    successful_files = []
    
    for file_path in files_to_process:
        logger.info(f"Generating tests for {file_path}...")
        
        # Put tests in a tests/generated/ folder matching the source structure
        output_dir = Path("tests/generated") / file_path.parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        stats = orchestrator.process_file(file_path, output_dir)
        
        if stats.get("tests_passed", 0) > 0:
            total_stats["tests_passed"] += stats["tests_passed"]
            total_stats["retries_used"] += stats.get("retries_used", 0)
            successful_files.append(file_path.name)
            
    # 5. Delivery
    if successful_files:
        pushed = commit_and_push(len(successful_files))
        
        if pushed:
            comment_body = (
                f"🤖 **AI-TestGen QA Report**\n\n"
                f"I noticed you updated some Python files! I autonomously generated and verified **{total_stats['tests_passed']}** new tests.\n"
                f"The tests have been committed to your branch.\n\n"
                f"**Files tested:**\n" + "\n".join([f"- `{f}`" for f in successful_files])
            )
            try:
                pr.create_issue_comment(comment_body)
                logger.info("Successfully pushed commits and left PR comment!")
            except Exception as e:
                logger.error(f"Failed to leave PR comment (commits were pushed): {e}")
    else:
        logger.info("No passing tests could be generated for the modified files.")


if __name__ == "__main__":
    main()
