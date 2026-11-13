"""Business invariants and counterexamples for the second portfolio batch."""
import csv
from datetime import date, timedelta
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from test_portfolio import module, rows, ROOT


def sample(prefix):
    path=next((ROOT/'projects').glob(prefix+'-*'))/'sample.csv'
    with path.open(newline='') as stream:
        return list(csv.DictReader(stream))


class PaymentLedger(unittest.TestCase):
    def test_exact_money_and_currency_separation(self):
        result=module('11').analyze([
            rows(event_id='1',batch_id='A',currency='USD',event_type='capture',amount_cents=101),
            rows(event_id='2',batch_id='A',currency='USD',event_type='fee',amount_cents=1),
            rows(event_id='3',batch_id='A',currency='USD',event_type='payout',amount_cents=100),
            rows(event_id='4',batch_id='A',currency='EUR',event_type='capture',amount_cents=50)])
        self.assertEqual(result['review_count'],1)
        usd=next(b for b in result['batches'] if b['currency']=='USD')
        self.assertEqual(usd['status'],'matched')
        self.assertEqual(usd['difference_cents'],0)

    def test_zero_expected_still_needs_payout_evidence(self):
        result=module('11').analyze([rows(event_id='1',batch_id='A',currency='USD',event_type='capture',amount_cents=0)])
        self.assertEqual(result['batches'][0]['reasons'],['missing_payout'])

    def test_duplicate_and_fractional_minor_units_rejected(self):
        data=sample('11')
        with self.assertRaises(ValueError): module('11').analyze(data+[data[0]])
        data[0]['amount_cents']='100.1'
        with self.assertRaises(ValueError): module('11').analyze(data)


class RevenueBridge(unittest.TestCase):
    def test_conservation_and_reactivation(self):
        result=module('12').analyze(sample('12'))
        september,october=result['bridges']
        self.assertEqual(september['movements_cents'],dict(new=5000,reactivation=0,expansion=2000,contraction=0,churn=8000))
        self.assertEqual(october['movements_cents'],dict(new=10000,reactivation=7000,expansion=0,contraction=3000,churn=0))
        self.assertAlmostEqual(october['net_revenue_retention'],14000/17000)
        self.assertTrue(all(b['bridge_difference_cents']==0 for b in result['bridges']))

    def test_missing_snapshot_is_not_churn(self):
        with self.assertRaises(ValueError): module('12').analyze(sample('12')[:-1])

    def test_gap_and_zero_opening(self):
        data=[rows(customer_id='A',month='2026-01',mrr_cents=0), rows(customer_id='A',month='2026-02',mrr_cents=100)]
        self.assertIsNone(module('12').analyze(data)['bridges'][0]['net_revenue_retention'])
        data[1]['month']='2026-03'
        with self.assertRaises(ValueError): module('12').analyze(data)


class OrderedFunnel(unittest.TestCase):
    def events(self, times):
        return [rows(event_id=str(i),session_id='S',event=e,timestamp=t) for i,(e,t) in enumerate(times)]

    def test_order_matters_and_later_retry_can_complete(self):
        data=self.events([('cart','2026-01-01T09:59:00Z'),('visit','2026-01-01T10:00:00Z'),('checkout','2026-01-01T10:01:00Z'),('purchase','2026-01-01T10:02:00Z')])
        self.assertEqual([x['sessions'] for x in module('13').analyze(data)['funnel']],[1,0,0,0])
        data.append(rows(event_id='retry',session_id='S',event='cart',timestamp='2026-01-01T10:00:30Z'))
        self.assertEqual([x['sessions'] for x in module('13').analyze(data)['funnel']],[1,1,1,1])

    def test_inclusive_window_and_timezone_equivalence(self):
        data=self.events([('visit','2026-01-01T10:00:00Z'),('cart','2026-01-01T05:10:00-05:00'),('checkout','2026-01-01T10:20:00Z'),('purchase','2026-01-01T10:30:00Z')])
        self.assertEqual(module('13').analyze(data)['funnel'][-1]['sessions'],1)
        data[-1]['timestamp']='2026-01-01T10:30:01Z'
        self.assertEqual(module('13').analyze(data)['funnel'][-1]['sessions'],0)

    def test_tied_timestamps_and_missing_visit(self):
        data=self.events([('visit','2026-01-01T10:00:00Z'),('cart','2026-01-01T10:00:00Z')])
        self.assertEqual(module('13').analyze(data)['funnel'][1]['sessions'],0)
        result=module('13').analyze(self.events([('purchase','2026-01-01T10:00:00Z')]))
        self.assertEqual(result['excluded_without_entry'],1)
        self.assertIsNone(result['funnel'][-1]['conversion_from_entry'])

    def test_unordered_input_is_stable(self):
        data=sample('13')
        self.assertEqual(module('13').analyze(data),module('13').analyze(list(reversed(data))))
        data[0]['timestamp']='2026-01-01T10:00:00'
        with self.assertRaises(ValueError): module('13').analyze(data)


class ChannelEconomics(unittest.TestCase):
    def test_roas_does_not_imply_positive_contribution(self):
        data=[rows(channel='A',revenue_cents=1000,refund_cents=100,cogs_cents=500,fulfillment_cents=100,ad_spend_cents=400,new_customers=2)]
        channel=module('14').analyze(data)['channels'][0]
        self.assertEqual(channel['gross_revenue_roas'],2.5)
        self.assertEqual(channel['contribution_after_acquisition_cents'],-100)
        self.assertEqual(channel['cac_cents'],200)

    def test_zero_denominators_and_invalid_refunds(self):
        data=[rows(channel='A',revenue_cents=0,refund_cents=0,cogs_cents=0,fulfillment_cents=0,ad_spend_cents=0,new_customers=0)]
        channel=module('14').analyze(data)['channels'][0]
        for key in ['gross_revenue_roas','contribution_margin','cac_cents']:
            self.assertIsNone(channel[key])
        data[0]['refund_cents']='1'
        with self.assertRaises(ValueError): module('14').analyze(data)


class InventoryPolicy(unittest.TestCase):
    def item(self, **changes):
        data=dict(sku='A',daily_mean=10,daily_std=0,lead_days=2,review_days=3,safety_z=0,on_hand=20,on_order=0,backorders=0,pack_size=12)
        data.update(changes)
        return rows(**data)

    def test_threshold_pack_rounding_and_backorders(self):
        result=module('15').analyze([self.item()])['items'][0]
        self.assertEqual(result['reorder_point'],20)
        self.assertEqual(result['order_up_to_target'],50)
        self.assertEqual(result['suggested_units'],36)
        self.assertEqual(module('15').analyze([self.item(on_hand=21)])['items'][0]['suggested_units'],0)
        result=module('15').analyze([self.item(on_hand=0,backorders=10)])['items'][0]
        self.assertEqual(result['suggested_units'],60)

    def test_zero_demand_and_invalid_safety_input(self):
        result=module('15').analyze([self.item(daily_mean=0,on_hand=0)])['items'][0]
        self.assertEqual(result['suggested_units'],0)
        with self.assertRaises(ValueError): module('15').analyze([self.item(safety_z='NaN')])
        with self.assertRaises(ValueError): module('15').analyze([self.item(pack_size=0)])


class ForecastBacktest(unittest.TestCase):
    def data(self, n=35):
        return [rows(date=(date(2026,1,1)+timedelta(days=i)).isoformat(),units=[10,20,30,40,50,60,70][i%7]) for i in range(n)]

    def test_seasonality_selected_on_validation(self):
        result=module('16').analyze(self.data())
        self.assertEqual(result['selected_model'],'seasonal_7')
        self.assertEqual(result['holdout_score']['mae'],0)
        self.assertTrue(all(p['trained_through'] < p['date'] for p in result['holdout_predictions']))

    def test_holdout_cannot_change_selection_or_earlier_predictions(self):
        data=self.data()
        before=module('16').analyze(data)
        data[-1]['units']='1000000'
        after=module('16').analyze(data)
        self.assertEqual(before['validation_scores'],after['validation_scores'])
        self.assertEqual(before['selected_model'],after['selected_model'])
        self.assertEqual([p['forecast'] for p in before['holdout_predictions']],[p['forecast'] for p in after['holdout_predictions']])

    def test_zero_series_and_missing_day(self):
        data=self.data()
        for row in data: row['units']='0'
        result=module('16').analyze(data)
        self.assertEqual(result['holdout_score']['mae'],0)
        self.assertIsNone(result['holdout_score']['wape'])
        with self.assertRaises(ValueError): module('16').analyze(data[:10]+data[11:])


class QueueSimulation(unittest.TestCase):
    def test_known_queue_and_sla_boundary(self):
        data=[rows(ticket_id='A',arrival_minute=0,service_minutes=10,wait_sla_minutes=0),rows(ticket_id='B',arrival_minute=0,service_minutes=5,wait_sla_minutes=10)]
        one,two=module('17').analyze(data,worker_counts=(1,2))['scenarios']
        self.assertEqual(one['mean_wait_minutes'],5)
        self.assertEqual(one['wait_sla_breach_rate'],0)
        self.assertEqual(two['mean_wait_minutes'],0)
        self.assertEqual(one['last_completion_minute'],15)

    def test_no_overlap_and_service_conservation(self):
        data=sample('17')
        for result in module('17').analyze(data)['scenarios']:
            finishes={}
            self.assertEqual(len(result['schedule']),len(data))
            for event in result['schedule']:
                self.assertGreaterEqual(event['start'],event['arrival'])
                self.assertGreaterEqual(event['start'],finishes.get(event['worker'],0))
                finishes[event['worker']]=event['finish']
            self.assertLessEqual(result['busy_fraction_from_time_zero'],1)

    def test_invalid_workers_and_zero_service(self):
        data=sample('17')
        with self.assertRaises(ValueError): module('17').analyze(data,worker_counts=(0,))
        data[0]['service_minutes']='0'
        with self.assertRaises(ValueError): module('17').analyze(data)


class UatTraceability(unittest.TestCase):
    def test_unmapped_critical_and_failed_requirement_hold(self):
        result=module('18').analyze(sample('18'))
        self.assertEqual(result['release_recommendation'],'hold')
        self.assertEqual(result['critical_blockers'],['R02','R06'])
        self.assertAlmostEqual(result['mapped_requirement_rate'],5/6)
        self.assertAlmostEqual(result['passed_requirement_rate'],2/6)

    def test_shared_test_counts_once_and_needs_consistent_result(self):
        data=[rows(requirement_id=r,priority='critical',test_id='T1',status='pass') for r in ['A','B']]
        result=module('18').analyze(data)
        self.assertEqual(result['unique_test_status_counts'],{'pass':1})
        self.assertEqual(result['release_recommendation'],'ready_for_human_signoff')
        data[1]['status']='fail'
        with self.assertRaises(ValueError): module('18').analyze(data)

    def test_placeholder_cannot_mask_mapped_test(self):
        data=[rows(requirement_id='A',priority='normal',test_id='',status='not_run'),rows(requirement_id='A',priority='normal',test_id='T1',status='pass')]
        with self.assertRaises(ValueError): module('18').analyze(data)


class ExposureConcentration(unittest.TestCase):
    def test_parent_consolidation_currency_and_zero_book(self):
        result={c['currency']:c for c in module('19').analyze(sample('19'))['currency_profiles']}
        self.assertEqual(result['USD']['groups'][0]['exposure_cents'],600000)
        self.assertAlmostEqual(result['USD']['hhi_fraction'],.445)
        self.assertAlmostEqual(result['EUR']['effective_group_count'],2)
        self.assertIsNone(result['GBP']['hhi_fraction'])
        self.assertFalse(result['GBP']['groups'][0]['review_flag'])

    def test_conflicting_parent_and_invalid_threshold(self):
        data=sample('19')
        data[1]['counterparty']=data[0]['counterparty'];data[1]['parent_group']='Other'
        with self.assertRaises(ValueError): module('19').analyze(data)
        with self.assertRaises(ValueError): module('19').analyze(sample('19'),review_threshold=2)


class MixAdjustment(unittest.TestCase):
    def test_simpson_reversal(self):
        result=module('20').analyze(sample('20'))
        self.assertAlmostEqual(result['pooled_difference'],-.38)
        self.assertAlmostEqual(result['standardized_difference'],.02)
        self.assertTrue(result['direction_reversal'])
        self.assertAlmostEqual(sum(s['common_weight'] for s in result['segments']),1)

    def test_proportional_split_invariance(self):
        data=sample('20');split=[]
        for row in data:
            for suffix in ['a','b']:
                split.append(dict(row,segment=row['segment']+suffix,users=str(int(row['users'])//2),conversions=str(int(row['conversions'])//2)))
        self.assertAlmostEqual(module('20').analyze(data)['standardized_difference'],module('20').analyze(split)['standardized_difference'])

    def test_missing_variant_and_invalid_counts(self):
        with self.assertRaises(ValueError): module('20').analyze(sample('20')[:-1])
        data=sample('20');data[0]['conversions']='1001'
        with self.assertRaises(ValueError): module('20').analyze(data)


class InputContracts(unittest.TestCase):
    def test_all_new_clis_reject_bad_headers_and_row_widths(self):
        with tempfile.TemporaryDirectory() as temp:
            for number in range(11,21):
                app=next((ROOT/'projects').glob(str(number)+'-*'))/'app.py'
                original=app.with_name('sample.csv').read_text().splitlines()
                for content in ['wrong,columns\n1,2\n','\n'.join([original[0],original[1]+',unexpected'])+'\n']:
                    with self.subTest(project=app.parent.name,content=content[:30]):
                        source=Path(temp)/'bad.csv';source.write_text(content)
                        output=Path(temp)/'output.json'
                        process=subprocess.run([sys.executable,str(app),'--input',str(source),'--output',str(output)],capture_output=True,text=True)
                        self.assertEqual(process.returncode,2,process.stderr)
                        self.assertFalse(output.exists())


if __name__=='__main__':
    unittest.main()
