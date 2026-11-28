"""The daily assistant's reports are player-facing Vietnamese; no database access."""
import ast
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REQUIRED={
 ('midas','Luyện Kim'),
 ('midas','Luyện Kim · Mua bằng Kim Cương'),
 ('dorm','Nhận tài nguyên Ký Túc Xá'),
 ('quiz','Câu Hỏi Hằng Ngày'),
 ('exam','Khảo Thí Học Viện · Quét Ải'),
 ('excursion','Thám Hiểm · Nhận tài nguyên'),
 ('excursion','Thám Hiểm · Mua Bánh Mì'),
 ('guild_sign','Bang Hội · Điểm Danh'),
 ('guild_order','Nhà Ăn · Bắt Đầu Đơn Hàng'),
 ('campaign','Nhận thưởng Chiến Dịch'),
 ('capsule','Triệu Hồi Thường'),
 ('senior','Triệu Hồi Cao Cấp'),
 ('mail','Nhận Thư'),
 ('internship','Thực Tập'),
 ('arena','Đấu Trường Sơ Cấp'),
 ('daily','Nhiệm Vụ Hằng Ngày'),
}

class GameAssistantVietnamese(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  tree=ast.parse((ROOT/'gxb2/engine.py').read_text(encoding='utf-8'))
  engine=next(t for t in tree.body if isinstance(t,ast.ClassDef) and t.name=='Engine')
  cls.method=next(t for t in engine.body if isinstance(t,ast.FunctionDef) and t.name=='assistant_run')

 def test_all_step_labels(self):
  labels=set()
  for node in ast.walk(self.method):
   if not isinstance(node,ast.Call) or not isinstance(node.func,ast.Name) or node.func.id!='step':continue
   if len(node.args)>1 and all(isinstance(x,ast.Constant) for x in node.args[:2]):
    labels.add((node.args[0].value,node.args[1].value))
  self.assertEqual(labels,REQUIRED)

 def test_spanish_and_english_errors_removed_from_assistant(self):
  raw=ast.get_source_segment((ROOT/'gxb2/engine.py').read_text(encoding='utf-8'),self.method)
  for fragment in ['Ya usada hoy','Ninguna terminada','Sin batallas gratis','Nada que reclamar',
                   'Sin intentos o sin dificultades superadas','Stage not cleared yet',
                   'Elige cuántos Raids','Todavía no hay recursos para recoger',
                   'No hay pedidos por empezar']:
   self.assertNotIn("'"+fragment+"'",raw)
  self.assertIn("Chưa có tài nguyên để thu thập",raw)

if __name__=='__main__':unittest.main()
