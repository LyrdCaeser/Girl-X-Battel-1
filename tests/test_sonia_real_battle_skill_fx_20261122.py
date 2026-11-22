"""End-to-end synthetic Lua report ensures the real attack is covered.

No Neon, player profile or production action is touched.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from gxb2.engine import Engine
from gxb2.battle import simulate,ONLINE_BATTLE_ID,normalize_online_seed


class SoniaBattleSkillFixture(unittest.TestCase):
    def test_native_lua_report_uses_supported_sonia_attack_id(self):
        with TemporaryDirectory(prefix='gxb3-sonia-fx-qa-') as folder:
            engine=Engine(Path(folder)/'qa.sqlite3')
            try:
                snapshot=engine.pvp_team_snapshot()
                team_a=[dict(unit) for unit in snapshot['team']]
                team_b=[dict(unit) for unit in snapshot['team']]
                team_a[0]['table_id']=758001
                for i,unit in enumerate(team_b):
                    unit['pos']=i+7
                report=simulate(
                    team_a,team_b,battle_id=ONLINE_BATTLE_ID,
                    seed=normalize_online_seed(123456),
                    chime_bonus_a=snapshot.get('chime_bonus'),
                    chime_bonus_b=snapshot.get('chime_bonus'))
                ids={int(f['skill_id']) for f in report['frames']
                     if int(f.get('pos') or 0)==1 and int(f.get('skill_id') or 0)>0}
                self.assertIn(75800100,ids,'real Sonia attack ID must be covered')
                src=(Path(__file__).resolve().parents[1]/'web/battle-animation.js').read_text()
                self.assertIn('75800100:{impact:',src)
                self.assertIn("at('lianhua_hurt01',.72,'target',1.6,.96)",src)
                self.assertIn('soniaNativeFx(skillId,caster,targets)',src)
            finally:
                engine.close()


if __name__=='__main__':
    unittest.main()
