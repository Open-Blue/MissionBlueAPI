import nox


@nox.session
def tests(session: nox.Session) -> None:
    """Run the test suite with coverage."""
    session.install("-r", "requirements.txt")
    # session.install("coverage[toml]")

    # Run tests with coverage
    session.run(
        "coverage",
        "run",
        "-m",
        "unittest",
        "discover",
        "-s",
        "tests",
        "-p",
        "*_test.py",
    )

    # Generate coverage report
    session.run("coverage", "report", "--fail-under=85")

    # Generate XML report for Codecov
    session.run("coverage", "xml")

    # Generate HTML report for local viewing
    session.run("coverage", "html")


@nox.session
def format(session: nox.Session) -> None:
    """Format code with black."""
    session.install("black")
    session.run("black", ".")


@nox.session
def lint(session: nox.Session) -> None:
    """Run linting checks."""
    session.install("ruff")
    session.run("ruff", "check", "--fix", ".")


# @nox.session
# def type_check(session: nox.Session) -> None:
#     """Run type checking with mypy."""
#     session.install("-r", "requirements.txt")
#     session.install("mypy")
#     session.run("mypy", ".")


# @nox.session
# def safety(session: nox.Session) -> None:
#     """Check dependencies for known security vulnerabilities."""
#     session.install("safety")
#     session.run("safety", "scan", "--full-report")
