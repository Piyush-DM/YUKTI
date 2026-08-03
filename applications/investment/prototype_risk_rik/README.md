# Prototype Risk RIK

This package contains a prototype-only executable vertical slice:

```text
case material -> execution request -> Risk RIK -> validated structured artifact -> prototype UI
```

It is deliberately isolated under `applications/investment/`. It does not
define DAALE engine architecture, production provider contracts, persistence,
or orchestration.

## Configuration

For deterministic development execution without external credentials:

```powershell
$env:YUKTI_PROTOTYPE_RISK_RIK_PROVIDER = "deterministic"
```

The deterministic provider is rule-based test machinery. It exercises:

```text
UI -> endpoint -> Risk RIK executor -> provider adapter -> artifact validation -> UI
```

It does not represent live model reasoning.

For live OpenAI model execution:

```powershell
$env:YUKTI_PROTOTYPE_RISK_RIK_PROVIDER = "openai"
$env:YUKTI_PROTOTYPE_RISK_RIK_MODEL = "<model supporting structured outputs>"
$env:OPENAI_API_KEY = "<secret>"
```

Optional:

```powershell
$env:YUKTI_PROTOTYPE_RISK_RIK_ENDPOINT = "https://api.openai.com/v1/responses"
```

The prototype refuses to execute without an explicit provider. The OpenAI
provider also requires model and API key configuration.

## Run

Serve the UI and local prototype endpoint:

```powershell
$env:YUKTI_PROTOTYPE_RISK_RIK_PROVIDER = "deterministic"
python -m applications.investment.prototype_risk_rik.server
```

Then open:

```text
http://127.0.0.1:8765/
```

The existing static fixture UI still opens directly through
`applications/investment/prototype-ui/index.html`. The executable Risk RIK path
requires the local prototype server because browser JavaScript cannot safely
hold model credentials.
