import csv
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
def module(prefix):
    path = next((ROOT / 'projects').glob(prefix + '-*')) / 'app.py'
    spec = importlib.util.spec_from_file_location('project_' + prefix, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def rows(**kwargs):
    return {k: str(v) for k,v in kwargs.items()}

class BusinessRules(unittest.TestCase):
    def test_reconciliation_tolerance_and_duplicate(self):
        app = module('01')
        base = [rows(source=s,trade_id='T1',amount=a) for s,a in [('bank','1.00'),('broker','1.01'),('client','1.00')]]
        self.assertEqual(app.analyze(base)['matched'], 1)
        self.assertIn('duplicate_reference', app.analyze(base+[base[0]])['exceptions'][0]['reasons'])
        self.assertEqual(app.analyze(base[:1])['exceptions'][0]['missing'], ['broker','client'])

    def test_reconciliation_nonfinite_rejected(self):
        with self.assertRaises(ValueError):
            module('01').analyze([rows(source='bank',trade_id='T',amount='NaN')])

    def test_sla_boundary_and_excess(self):
        result = module('02').analyze([rows(case_id='1',stage='approve',minutes=20,sla_minutes=20),rows(case_id='2',stage='approve',minutes=30,sla_minutes=20)])
        self.assertEqual(result['stages'][0]['breach_rate'], .5)
        self.assertEqual(result['stages'][0]['excess_minutes'], 10)
        self.assertEqual(result['stages'][0]['p90_minutes'], 30)

    def test_sla_duplicate_is_not_double_counted(self):
        row = rows(case_id='1',stage='approve',minutes=20,sla_minutes=20)
        with self.assertRaises(ValueError):
            module('02').analyze([row,row])

    def test_risk_gate_overrides_benefit(self):
        app=module('03')
        result=app.analyze([rows(workflow='huge',daily_cases=10000,minutes_saved=20,build_hours=1,risk=5,approval_control=1)])
        self.assertEqual(result['ranked_workflows'][0]['recommendation'],'hold')
        self.assertEqual(result['ranked_workflows'][0]['priority_score'],0)

    def test_zero_benefit_payback(self):
        result=module('03').analyze([rows(workflow='zero',daily_cases=0,minutes_saved=20,build_hours=1,risk=1,approval_control=1)])
        self.assertIsNone(result['ranked_workflows'][0]['payback_workdays'])
        self.assertEqual(result['ranked_workflows'][0]['recommendation'],'hold')

    def test_rfm_thresholds(self):
        result=module('04').analyze([rows(customer_id='A',last_purchase='2026-10-01',orders=10,spend=1000)])
        self.assertEqual(result['customers'][0]['segment'],'champions')
        with self.assertRaises(ValueError):
            module('04').analyze([rows(customer_id='A',last_purchase='2026-11-01',orders=10,spend=1000)])

    def test_cohort_customer_not_order_denominator(self):
        data=[rows(order_id='1',customer_id='A',order_date='2026-09-01'), rows(order_id='2',customer_id='A',order_date='2026-09-02'), rows(order_id='3',customer_id='B',order_date='2026-09-01'), rows(order_id='4',customer_id='A',order_date='2026-10-01')]
        cohort=module('05').analyze(data)['cohorts'][0]
        self.assertEqual(cohort['size'],2)
        self.assertEqual([p['retention'] for p in cohort['periods']],[1,.5])
        self.assertEqual(len(cohort['periods']),2)

    def test_cohort_year_boundary(self):
        data=[rows(order_id='1',customer_id='A',order_date='2025-12-01'),rows(order_id='2',customer_id='A',order_date='2026-01-01')]
        result=module('05').analyze(data,cutoff='2026-01-31')
        self.assertEqual(result['cohorts'][0]['cohort'],'2025-12')
        self.assertEqual(len(result['cohorts'][0]['periods']),2)

    def test_experiment_equal_rates(self):
        result=module('06').analyze([rows(variant=v,visitors=1000,conversions=100) for v in ['control','treatment']])
        self.assertEqual(result['two_sided_p_value'],1)
        self.assertEqual(result['decision'],'inconclusive')
        self.assertLess(result['difference_ci95'][0],0)

    def test_sparse_experiment_suppresses_inference(self):
        result=module('06').analyze([rows(variant=v,visitors=100,conversions=0) for v in ['control','treatment']])
        self.assertIsNone(result['relative_lift'])
        self.assertIsNone(result['difference_ci95'])
        self.assertIsNone(result['two_sided_p_value'])

    def test_sample_ratio_mismatch(self):
        result=module('06').analyze([rows(variant='control',visitors=1000,conversions=100),rows(variant='treatment',visitors=2000,conversions=400)])
        self.assertEqual(result['decision'],'investigate_allocation')

    def test_crm_blanks_do_not_match(self):
        result=module('07').analyze([rows(record_id=k,email='',phone='') for k in ['A','B']])
        self.assertEqual(result['review_groups'],[])
        self.assertEqual(result['automatic_merges'],0)

    def test_crm_conflict_is_flagged(self):
        result=module('07').analyze([rows(record_id='A',email='a@example.invalid',phone='1234567890'),rows(record_id='B',email='b@example.invalid',phone='1234567890')])
        self.assertEqual(result['review_groups'][0]['status'],'conflicting_identifiers')

    def test_savings_zero_growth(self):
        result=module('08').analyze([rows(scenario='flat',initial=100,monthly_contribution=10,annual_return=0,annual_fee=0,inflation=0,years=1)])
        year=result['scenarios'][0]['annual_schedule'][0]
        self.assertEqual(year['nominal_balance'],220)
        self.assertEqual(year['real_balance'],220)

    def test_savings_effective_annual_growth(self):
        result=module('08').analyze([rows(scenario='growth',initial=100,monthly_contribution=0,annual_return=.1,annual_fee=0,inflation=.1,years=1)])
        year=result['scenarios'][0]['annual_schedule'][0]
        self.assertEqual(year['nominal_balance'],110)
        self.assertEqual(year['real_balance'],100)

    def test_basketball_three_pointer_and_uncertainty(self):
        result=module('09').analyze([rows(shot_id='1',player='A',zone='three',made=1)])['shot_profiles'][0]
        self.assertEqual(result['points_per_attempt'],3)
        self.assertEqual(result['effective_fg_pct'],1.5)
        self.assertLess(result['fg_wilson_ci95'][0],1)
        self.assertTrue(result['small_sample'])

    def test_golf_partial_round_and_no_missed_greens(self):
        result=module('10').analyze([rows(round_id='A',hole=1,par=4,strokes=4,putts=2,gir=1)])['rounds'][0]
        self.assertFalse(result['complete_round'])
        self.assertIsNone(result['par_or_better_after_missed_gir'])
        self.assertEqual(result['relative_to_par'],0)

class EndToEnd(unittest.TestCase):
    def test_all_projects_reproduce_committed_results(self):
        with tempfile.TemporaryDirectory() as temp:
            for path in sorted((ROOT/'projects').glob('*/app.py')):
                with self.subTest(project=path.parent.name):
                    output=Path(temp)/'result.json'
                    process=subprocess.run([sys.executable,str(path),'--output',str(output)],capture_output=True,text=True)
                    self.assertEqual(process.returncode,0,process.stderr)
                    self.assertEqual(json.loads(output.read_text()),json.loads(path.with_name('results.json').read_text()))

    def test_all_clis_reject_header_only_input(self):
        with tempfile.TemporaryDirectory() as temp:
            for path in sorted((ROOT/'projects').glob('*/app.py')):
                with self.subTest(project=path.parent.name):
                    empty=Path(temp)/'empty.csv'
                    empty.write_text(path.with_name('sample.csv').read_text().splitlines()[0]+'\n')
                    process=subprocess.run([sys.executable,str(path),'--input',str(empty),'--output',str(Path(temp)/'out.json')],capture_output=True,text=True)
                    self.assertEqual(process.returncode,2)
                    self.assertIn('at least one',process.stderr)

if __name__=='__main__':
    unittest.main()
