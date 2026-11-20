"""Checks Daily Quiz labels and original artwork aspect ratio on small screens."""
import re
import unittest
from pathlib import Path
from gxb2.engine import Engine
from tempfile import TemporaryDirectory


class DailyQuizVisualRules(unittest.TestCase):
    def test_translated_categories_and_intrinsic_art(self):
        with TemporaryDirectory() as d:
            e=Engine(Path(d)/'quiz.sqlite3')
            state=e._load()
            names=[row['name'] for row in e.daily_quiz_info(state)['categories']]
            e.close()
        self.assertEqual(names,['Tài Nguyên','Kinh Nghiệm','Mảnh Nữ Thần'])
        css=Path('web/daily-quiz-mobile-fix.css').read_text()
        self.assertIn('aspect-ratio:641/253',css)
        self.assertIn('@media(max-width:720px)',css)
        self.assertIn('background-size:100% 100%',css)

    def test_link_and_ui(self):
        index=Path('web/index.html').read_text()
        assert 'daily-quiz-mobile-fix.css?v=20261116-r1' in index
        assert 'Thử Thách Hằng Ngày' in index
        js=Path('web/app.js').read_text()
        self.assertIn('Tài Nguyên',Path('gxb2/engine.py').read_text())
        self.assertIn("tier.cleared?\"Nhận\":'Chiến Đấu'",js)


if __name__=='__main__':
    unittest.main()
