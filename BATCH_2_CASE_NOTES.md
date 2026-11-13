# Second-batch case notes

These observations are snapshots of the bundled **synthetic** CSV fixtures, not real-world business results. Regenerate JSON with `python3 run_all.py`; if inputs change, revise these explanatory notes as well. All money below is in the input's integer minor units.

For financial operations roles, start with 11, 12, and 19. For growth/product analytics, start with 13, 14, and 20. For business operations and business analyst roles, start with 15, 16, 17, and 18. Be ready to explain assumptions and tests before presenting any case as your work.

## 11. [Payment Settlement Ledger](projects/11-payment-settlement-ledger/README.md)

The sample contains 5 batch/currency combinations, of which 3 require review. One batch is short by 500 minor units; another lacks payout evidence; a refund-only batch has a negative expected settlement. The same batch label in EUR and USD is reconciled separately.

**Interview discussion:** Why is a zero expected settlement not sufficient evidence that a batch has settled? Which adjustments would need their own ledger event type?

## 12. [Subscription Revenue Bridge](projects/12-subscription-revenue-bridge/README.md)

October MRR rises from 17,000 to 31,000 minor units. This consists of 10,000 new MRR, 7,000 reactivated MRR, and 3,000 contraction. Existing-account net revenue retention is 82.4%; total growth therefore does not mean every retention metric improved. Both monthly bridges balance to zero.

**Interview discussion:** How could a missing customer snapshot be mistaken for churn, and why does the input require an explicit zero?

## 13. [Ordered Checkout Funnel](projects/13-ordered-checkout-funnel/README.md)

Of 63 observed sessions, 1 has no entry event. Valid stage counts are 62 → 50 → 38 → 25. Entry-to-purchase conversion is 40.3%. A purchase after 45 minutes is excluded from the 30-minute funnel; an out-of-order cart does not count unless a later cart completes the sequence.

**Interview discussion:** What would change if the funnel were user-based instead of session-based, or if a new visit restarted the conversion window?

## 14. [Acquisition Channel Contribution](projects/14-acquisition-unit-economics/README.md)

Paid social has gross-revenue ROAS of 2.77 but contribution after acquisition of -110,000 minor units. Revenue alone hides refunds, merchandise costs, fulfillment, and advertising. Total sample contribution is 610,000 minor units; this is before fixed overhead.

**Interview discussion:** Why is attributed ROAS not proof of incremental return, and what extra data would support a lifetime-value analysis?

## 15. [Inventory Reorder Policy Simulator](projects/15-inventory-reorder-policy/README.md)

JACKET has inventory position 48 against a reorder threshold of 102. The coverage target is 193, but case packing produces a recommendation of 156 units (13 cases), taking position to 204. TEE is above threshold and receives no order. Zero-demand CAP receives zero units.

**Interview discussion:** When would independent daily demand and deterministic lead time make the safety-stock formula misleading?

## 16. [Demand Forecast Backtest](projects/16-demand-forecast-backtest/README.md)

The validation window selects `seasonal_7`. The separate seven-day holdout has MAE 2.29 units and WAPE 4.6%. Each output row records the latest permitted training date. Changing the final holdout observation cannot change the chosen model or any forecast in that holdout.

**Interview discussion:** How does rolling one-day-ahead evaluation differ from forecasting an entire week at a single origin? Why should model selection avoid the holdout?

## 17. [Service Queue Capacity Simulator](projects/17-service-queue-simulation/README.md)

Replaying the same 40 tickets gives mean waits of 95.05 minutes with 1 worker(s), 17.65 minutes with 2 worker(s), 0.38 minutes with 3 worker(s). Three workers eliminate wait-SLA breaches in this sample. This is a scenario result, not an economically optimal staffing recommendation.

**Interview discussion:** Which missing factors—shift availability, priorities, abandonment, service-time uncertainty—could change the conclusion?

## 18. [UAT Requirements Traceability](projects/18-uat-release-readiness/README.md)

Mapped-requirement coverage is 83.3%, but fully passed-requirement coverage is only 33.3%. Critical blockers are R02, R06. The recommendation is `hold`; merely having a linked test does not mean a requirement has passed.

**Interview discussion:** How would you select the latest valid test run while preserving evidence and preventing stale passes from masking new failures?

## 19. [Counterparty Exposure Concentration](projects/19-counterparty-concentration/README.md)

After related entities are grouped, Alpha represents 60% of USD exposure. USD concentration is HHI 0.445, equivalent to approximately 2.25 equally sized groups. EUR is evaluated separately, and the all-zero GBP book receives null concentration measures.

**Interview discussion:** Why must entity hierarchy, currency conversion, collateral, and gross-versus-net exposure be defined before making a risk claim?

## 20. [Campaign Mix and Simpson Reversal](projects/20-campaign-mix-adjustment/README.md)

Treatment minus control is -38.0 percentage points in the raw pool, but +2.0 points under the common combined-customer mix. Treatment is 2 points higher within each segment; unequal segment proportions reverse the aggregate result. Standardization makes the comparison more interpretable but does not by itself identify a causal effect.

**Interview discussion:** Why must segment definitions be set before observing outcomes, and why could post-treatment segments bias an adjusted analysis?
