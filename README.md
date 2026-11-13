# Leo Li · Business Analytics Portfolio

Ten runnable case studies connecting securities operations, retail CRM, financial education, basketball, and golf. Built with Python's standard library, with SQLite examples for operational KPIs and retention cohorts.

These are independent portfolio prototypes built with synthetic data. They are not past employer systems, production deployments, or evidence of realized business impact. The code is intended to be inspected, tested, and extended.

## Start here

```sh
python3 run_all.py
python3 -m unittest discover -s tests -v
```

Requires Python 3.10 or newer. No pip installation, network connection, credentials, or paid service is needed. Each project also runs independently with `python3 app.py` from its own directory. Output paths default to the project directory; pass `--output` to save elsewhere.

## Projects

| Project | Business question |
| --- | --- |
| [Securities Reconciliation Engine](projects/01-securities-reconciliation/README.md) | Which transaction breaks should operations investigate before settlement? |
| [Settlement SLA and Bottleneck Analysis](projects/02-settlement-sla/README.md) | Where does a settlement workflow lose time? |
| [Automation Opportunity Scorecard](projects/03-automation-prioritization/README.md) | Which workflow changes deserve a pilot, and which fail control gates? |
| [Retail Customer Lifecycle Segmentation](projects/04-retail-rfm/README.md) | Which customers should a CRM team retain, reactivate, or develop? |
| [Monthly Purchase Retention Cohorts](projects/05-retention-cohorts/README.md) | Do newly acquired customers return in later months? |
| [Campaign A/B Test Readout](projects/06-campaign-experiment/README.md) | Does a campaign change conversion enough to justify a follow-up experiment? |
| [CRM Identity Quality Audit](projects/07-crm-identity-quality/README.md) | Which member records can be linked exactly and which need manual review? |
| [Financial Education Savings Simulator](projects/08-savings-scenarios/README.md) | How do contributions, compounding, fees, and inflation change a hypothetical savings path? |
| [Basketball Shot Profile Analytics](projects/09-basketball-shot-profile/README.md) | Which shot zones combine efficiency and enough attempts to merit attention? |
| [Golf Round Performance Review](projects/10-golf-round-review/README.md) | Which parts of a round deserve focused practice? |

## Suggested review order

Start with **Securities Reconciliation** to inspect exception handling and monetary precision. Follow with **Campaign A/B Test Readout** for statistical assumptions and guardrails, then **Retention Cohorts** for denominator discipline and SQL/Python parity. Basketball and golf add personal context and demonstrate transferring analytical methods to another domain.

Every folder includes a documented input schema, synthetic CSV fixture, executable analysis, and reproducible JSON output. Two folders also include SQLite queries. The tests cover business boundaries, duplicate handling, sparse experiments, date boundaries, financial arithmetic, SQL parity, and CLI reproducibility.

## Repository layout

- `projects/`: ten self-contained case studies.
- `tests/`: business-rule and end-to-end tests.
- `run_all.py`: regenerate all bundled results.
- `catalog.json`: machine-readable project index.
- `.github/workflows/ci.yml`: GitHub Actions checks for Python 3.10 and 3.13.
- `START_HERE_ZH.md`: Chinese walkthrough and publication status.

## Evidence and limitations

Local validation used Python 3.13.6. The GitHub Actions workflow is prepared but has not run remotely. Bundled data is intentionally small enough to inspect; it is not a performance benchmark. Input validation is suitable for these prototypes, not a full production ingestion or security boundary. Do not load sensitive records into a public repository.

## Development priorities

1. Reconciliation: multi-currency keys, input schemas, reviewer audit trails, larger benchmark fixtures.
2. Marketing: randomized user-level observations, power planning, campaign eligibility and consent rules.
3. Retention: completeness checks, acquisition sources, and gross-margin outcomes.
4. Sports: shot-level context, real licensed datasets, and interactive visual exploration.

No real employer data, résumé contact details, or proprietary code is included. No third-party dataset is required. No open-source license has been selected yet.
