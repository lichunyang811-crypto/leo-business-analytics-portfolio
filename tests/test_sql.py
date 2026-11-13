import csv
import json
from pathlib import Path
import sqlite3
from contextlib import closing
import unittest

ROOT=Path(__file__).resolve().parents[1]
class SqlParity(unittest.TestCase):
    def test_sql_matches_python_on_bundled_data(self):
        for slug, table in [('02-settlement-sla','observations'),('05-retention-cohorts','orders')]:
            with self.subTest(project=slug), closing(sqlite3.connect(':memory:')) as connection:
                path=ROOT/'projects'/slug
                with (path/'sample.csv').open() as stream:
                    reader=csv.reader(stream)
                    columns=next(reader)
                    connection.execute(f'CREATE TABLE {table} ('+', '.join(f'{c} TEXT' for c in columns)+')')
                    connection.executemany(f'INSERT INTO {table} VALUES ('+','.join('?' for _ in columns)+')',reader)
                result=connection.execute((path/'analysis.sql').read_text()).fetchall()
                expected=json.loads((path/'results.json').read_text())
                if table=='observations':
                    self.assertEqual(len(result),len(expected['stages']))
                    for actual, stage in zip(result,expected['stages']):
                        self.assertEqual(actual[0],stage['stage'])
                        for value,key in zip(actual[1:],['observations','mean_minutes','breach_rate','excess_minutes']):
                            self.assertAlmostEqual(value,stage[key])
                else:
                    flattened=[(c['cohort'],c['size'],p['active_customers'],p['retention']) for c in expected['cohorts'] for p in c['periods']]
                    self.assertEqual([(r[0],r[2],r[3],r[4]) for r in result],flattened)
