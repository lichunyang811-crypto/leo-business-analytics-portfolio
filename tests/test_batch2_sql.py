import csv
import json
from pathlib import Path
import sqlite3
from contextlib import closing
import unittest
from test_portfolio import ROOT


class SecondBatchSql(unittest.TestCase):
    def query(self, slug, table):
        folder=ROOT/'projects'/slug
        with closing(sqlite3.connect(':memory:')) as connection:
            connection.row_factory=sqlite3.Row
            with (folder/'sample.csv').open(newline='') as stream:
                reader=csv.reader(stream);headers=next(reader)
                connection.execute(f'CREATE TABLE {table} ('+', '.join(f'{h} TEXT' for h in headers)+')')
                connection.executemany(f'INSERT INTO {table} VALUES ('+','.join('?' for h in headers)+')',reader)
            result=[dict(r) for r in connection.execute((folder/'analysis.sql').read_text())]
        return result,json.loads((folder/'results.json').read_text())

    def test_revenue_window_functions_match_python(self):
        actual,expected=self.query('12-subscription-revenue-bridge','snapshots')
        self.assertEqual(len(actual),len(expected['bridges']))
        for row,bridge in zip(actual,expected['bridges']):
            for field in ['month','opening_mrr_cents','closing_mrr_cents']:
                self.assertEqual(row[field],bridge[field])
            for movement,value in bridge['movements_cents'].items():
                self.assertEqual(row[movement+'_cents'],value)
            self.assertAlmostEqual(row['net_revenue_retention'],bridge['net_revenue_retention'])

    def test_mix_adjustment_sql_matches_python(self):
        actual,expected=self.query('20-campaign-mix-adjustment','cells')
        self.assertEqual(len(actual),2)
        for row in actual:
            self.assertAlmostEqual(row['pooled_rate'],expected['pooled_rates'][row['variant']])
            self.assertAlmostEqual(row['standardized_rate'],expected['standardized_rates'][row['variant']])


if __name__=='__main__': unittest.main()
