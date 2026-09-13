import unittest, tempfile, sys, io
from pathlib import Path
from unittest.mock import patch
import main
class ScopeTests(unittest.TestCase):
 def test_local_text_does_not_upload(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp)/'sample.md';p.write_text('public sample',encoding='utf-8')
   with patch.object(sys,'argv',['main.py',str(p)]), patch('main.subprocess.run') as run, patch('sys.stdout',new_callable=io.StringIO) as output:
    main.main();run.assert_not_called();self.assertIn('public sample',output.getvalue())
 def test_public_url_extracts_without_upload(self):
  with patch.object(sys,'argv',['main.py','https://example.org/article']), patch('scripts.fetch_url.fetch',return_value='public text') as fetch, patch('main.subprocess.run') as run, patch('sys.stdout',new_callable=io.StringIO):
   main.main();fetch.assert_called_once();run.assert_not_called()
 def test_remote_mode_needs_upload(self):
  with patch.object(sys,'argv',['main.py','https://example.org','--deep-analysis']), patch('main.subprocess.run') as run:
   with self.assertRaises(SystemExit):main.main()
   run.assert_not_called()
 def test_notebook_upload_does_not_authorize_getnote(self):
  with patch.object(sys,'argv',['main.py','https://xiaoyuzhoufm.com/episode/demo','--upload']), patch('main.subprocess.run') as run:
   with self.assertRaises(SystemExit):main.main()
   run.assert_not_called()
if __name__=='__main__':unittest.main()
