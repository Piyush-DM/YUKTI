# DAALE Tests

This directory contains tests for the DAALE implementation scaffold.

The current tests intentionally avoid validating ontology behavior because the
architecture has not approved that behavior yet. Instead, they protect
repository stability by checking that named modules import successfully and
remain documented.

Run the suite from the repository directory:

```powershell
python -m unittest discover -s daale/tests
```
