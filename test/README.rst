Overview of the subdirectories below:

    - test_code: general bad coding practice detection
    - test_design: detection of code that violates pyam design decisions
    - test_doctest: test code documentation
    - test_smoke: smoke tests
    - test_system: system-level tests
    - test_test: tests that test the rest of the tests (including test coverage)
    - test_unit: unit tests

Some of the tests have additional external dependencies, which are listed below:

    - mockito (http://pypi.python.org/pypi/mockito)
    - MySQL server
    - GNU parallel
    - pep8
    - pexpect
    - Pylint
    - Pyflakes
    - PyEnchant
    - Snakefood (http://furius.ca/snakefood)
