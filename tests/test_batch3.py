import csv
import tempfile
import unittest
from pathlib import Path
from test_portfolio import module, ROOT


class SqlCases(unittest.TestCase):
    def run_case(self, prefix, records):
        app = module(prefix)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'records.csv'
            with path.open('w', newline='') as stream:
                w = csv.writer(stream)
                w.writerow(app.FIELDS)
                w.writerows(records)
            return app.run(path)

    def test_month_end_excludes_future_clearing(self):
        result = self.run_case('21', [('1','x','2026-10-31','credit',200),
                                      ('2','x','2026-11-01','debit',200)])
        self.assertEqual((result[0]['net_cents'],result[0]['age_days']),(-200,0))

    def test_consent_tie_and_contact_boundary(self):
        result = self.run_case('22',[('1','x','2026-10-31','opt_out'),
                                     ('2','x','2026-10-31','opt_in'),
                                     ('3','y','2026-09-01','opt_in'),
                                     ('4','y','2026-10-24','send')])
        self.assertEqual([r['decision'] for r in result],['opted_out','eligible'])

    def test_singletons_and_repeated_lines(self):
        result = self.run_case('23',[('1','x','a'),('2','x','a'),('3','x','b'),
                                     ('4','y','a'),('5','y','b'),('6','z','c')])
        self.assertEqual(len(result),1)
        self.assertEqual(result[0]['together'],2)
        self.assertAlmostEqual(result[0]['lift'],1.5)
