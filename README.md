To go to the tutorial for research project (CI/CD for AWS Lambda), go [here](./research/TUTORIAL.md)

### Python project setup

To run the project
```
python3 -m blueprint
```
Enforcing PEP8 standards:
A pre-commit hook is configured to automatically enforce the PEP-8 standards using yapf. 

To run unit tests
```
pytest
```
It runs the test contained in the file test_app.py

Example output of failed test:
```
=========================================================================== FAILURES ============================================================================
___________________________________________________________________________ test_app ____________________________________________________________________________

capsys = <_pytest.capture.CaptureFixture object at 0x10d1481d0>, example_fixture = None

    def test_app(capsys, example_fixture):
        # pylint: disable=W0612,W0613
        blueprint.Blueprint.run()
        captured = capsys.readouterr()
    
>       assert "Hello World.." == captured.out
E       AssertionError: assert 'Hello World..' == 'Hello World...\n'
E         - Hello World...
E         ?              --
E         + Hello World..

tests/test_app.py:9: AssertionError
---------------------------------------------------------------------- Captured log setup -----------------------------------------------------------------------
INFO     tests.conftest:conftest.py:9 Setting Up Example Fixture...
--------------------------------------------------------------------- Captured log teardown ---------------------------------------------------------------------
INFO     tests.conftest:conftest.py:11 Tearing Down Example Fixture...

---------- coverage: platform darwin, python 3.7.5-final-0 -----------

==================================================================== short test summary info ====================================================================
FAILED tests/test_app.py::test_app - AssertionError: assert 'Hello World..' == 'Hello World...\n'
======================================================================= 1 failed in 0.10s =======================================================================
```
Example output of successful test:
```
------------------------------------------------------------------------ live log setup -------------------------------------------------------------------------
2020-05-01 01:04:03 [    INFO] Setting Up Example Fixture... (conftest.py:9)
PASSED                                                                                                                                                    [100%]
----------------------------------------------------------------------- live log teardown -----------------------------------------------------------------------
2020-05-01 01:04:03 [    INFO] Tearing Down Example Fixture... (conftest.py:11)
Coverage.py warning: No data was collected. (no-data-collected)
WARNING: Failed to generate report: No data to report.

/Users/akashmalhotra/PycharmProjects/CC_Project/venv/lib/python3.7/site-packages/pytest_cov/plugin.py:254: PytestWarning: Failed to generate report: No data to report.

  self.cov_controller.finish()


---------- coverage: platform darwin, python 3.7.5-final-0 -----------


======================================================================= 1 passed in 0.07s =======================================================================
```

### Infrastructure setup
1. All IaC go into Terraform folder
2. We create build pipeline also using terraform
Note how variables are passed in
```shell script
terraform init
terraform apply -var="github_personal_token=1111aaaaa" -var="github_username=username"
```
Verify plan shown and accept it with `yes`
