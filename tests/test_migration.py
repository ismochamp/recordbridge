"""Behavior-focused checks against the compiled C++ engine and local adapter."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from server import execute

class MigrationTests(unittest.TestCase):
    def run_engine(self, text, mapping=None, existing=None, raw=False, same_path=False):
        with tempfile.TemporaryDirectory() as work:
            work=Path(work); source=work/'source.csv'; output=source if same_path else work/'out.json'
            source.write_bytes(text if raw else text.encode('utf-8'))
            original=source.read_bytes()
            if existing is not None: output.write_text(existing)
            args=[str(ROOT/'build'/('migrator.exe' if sys.platform=='win32' else 'migrator')),'--input',str(source),'--output',str(output)]
            if mapping is not None:
                schema=work/'mapping.tsv';schema.write_text(mapping);args+=['--map',str(schema)]
            p=subprocess.run(args,capture_output=True,text=True)
            result=json.loads(p.stdout)
            self.assertEqual(p.returncode,0 if result['ok'] else 2)
            self.assertEqual(source.read_bytes(),original)
            data=output.read_text() if output.exists() else None
            leftovers=list(work.glob('*.tmp-*'))
            self.assertFalse(leftovers)
            return result,data

    def test_typed_fixture_and_quoted_multiline_fields(self):
        report,out=self.run_engine((ROOT/'fixtures/customers.csv').read_text(),(ROOT/'fixtures/mapping.tsv').read_text())
        self.assertTrue(report['ok']); data=json.loads(out)
        self.assertEqual(data[0]['company'],'Northwind, Studio')
        self.assertEqual(data[1]['notes'],'Two-line note:\nreview next quarter')
        self.assertEqual(data[2]['notes'],'UTF-8 and "quoted text" preserved')
        self.assertEqual(data[2]['company'],'Müller & Co.')
        self.assertIs(data[1]['is_active'],False)
        self.assertEqual(data[0]['customer_id'],1001)
        self.assertEqual(data[0]['credit_limit'],1250.50)

    def test_bom_crlf_and_blank_lines(self):
        report,out=self.run_engine('\ufeffid,name\r\n\r\n1,"A"\r\n')
        self.assertTrue(report['ok']);self.assertEqual(json.loads(out),[{'id':'1','name':'A'}])

    def test_unclosed_quote_blocks_export(self):
        report,out=self.run_engine('a,b\n1,"oops\n')
        self.assertFalse(report['ok']);self.assertIsNone(out)
        self.assertIn('Unclosed',report['errors'][0]['message'])

    def test_quote_in_unquoted_field_blocks_export(self):
        report,out=self.run_engine('a\nab"cd\n');self.assertFalse(report['ok']);self.assertIsNone(out)

    def test_character_after_closing_quote_blocks_export(self):
        report,out=self.run_engine('a\n"x"z\n');self.assertFalse(report['ok']);self.assertIsNone(out)

    def test_duplicate_headers_block_export(self):
        report,out=self.run_engine('a,a\n1,2\n');self.assertFalse(report['ok']);self.assertIsNone(out)

    def test_wrong_field_count_identifies_line(self):
        report,out=self.run_engine('a,b\n1\n');self.assertFalse(report['ok']);self.assertIsNone(out);self.assertEqual(report['errors'][0]['line'],2)

    def test_required_missing_column(self):
        report,out=self.run_engine('a\n1\n','missing\tvalue\tstring\ttrue\n');self.assertFalse(report['ok']);self.assertIsNone(out)

    def test_optional_empty_and_absent_values(self):
        report,out=self.run_engine('a,b\nx,\n','b\tvalue\tinteger\tfalse\nmissing\textra\tstring\tfalse\n')
        self.assertTrue(report['ok']);self.assertEqual(json.loads(out),[{'value':None,'extra':None}]);self.assertTrue(report['warnings'])

    def test_bad_types_and_overflow_block_entire_output(self):
        report,out=self.run_engine('id,active,amount\n9223372036854775808,maybe,NaN\n','id\tid\tinteger\ttrue\nactive\tactive\tboolean\ttrue\namount\tamount\tnumber\ttrue\n')
        self.assertFalse(report['ok']);self.assertEqual(len(report['errors']),3);self.assertIsNone(out)

    def test_duplicate_json_targets_block_export(self):
        report,out=self.run_engine('a,b\n1,2\n','a\tid\tinteger\ttrue\nb\tid\tinteger\ttrue\n');self.assertFalse(report['ok']);self.assertIsNone(out)

    def test_existing_output_is_never_replaced(self):
        report,out=self.run_engine('a\n1\n',existing='KEEP ME');self.assertFalse(report['ok']);self.assertEqual(out,'KEEP ME')

    def test_input_cannot_be_its_own_output(self):
        report,out=self.run_engine('a\n1\n',same_path=True);self.assertFalse(report['ok']);self.assertEqual(out,'a\n1\n')

    def test_invalid_utf8_is_rejected(self):
        report,out=self.run_engine(b'a\n\xff\n',raw=True);self.assertFalse(report['ok']);self.assertIsNone(out)

    def test_dashboard_adapter_runs_real_engine(self):
        result=execute('id,active\n7,yes\n',[{'source':'id','target':'identifier','type':'integer','required':True},{'source':'active','target':'enabled','type':'boolean','required':True}])
        self.assertTrue(result['ok']);self.assertEqual(result['preview'],[{'identifier':7,'enabled':True}]);self.assertEqual(json.loads(result['output']),result['preview'])

    def test_dashboard_rejects_mapping_delimiter_injection(self):
        with self.assertRaises(ValueError):execute('a\n1\n',[{'source':'a','target':'x\ty','type':'string','required':False}])

if __name__=='__main__':unittest.main(verbosity=2)
