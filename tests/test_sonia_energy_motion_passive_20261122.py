"""Regression: native EP meter and Sonia animated movement/passive visual cues.

Visual-only: never mutate combat stats or create synthetic battle rewards.
"""
import json
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]

class EnergyMotionPassiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app=(ROOT/'web/app.js').read_text()
        cls.battle=(ROOT/'web/battle-animation.js').read_text()
        cls.css=(ROOT/'web/style.css').read_text()
        cls.html=(ROOT/'web/index.html').read_text()
        cls.model=json.loads((ROOT/'web/assets/chibis/lyr_sonia/model.json').read_text())

    def test_ep_meters_are_attached_to_each_real_fighter_and_read_lua_eps(self):
        for text in (
            "const epBar=node('div','unit-ep'),epFill=node('i')",
            "epBar.setAttribute('aria-label','Năng lượng')",
            "epFill,ep:0",
            "for(const e of list(frame.eps))",
            "const epValue=Number(e.ep),epPos=Number(e.pos)",
            "Number.isFinite(epValue)",
            "if(epPos===13)progressFill.style.width=amount+'%'",
            "if(epPos>=1&&epPos<=12)",
            "fighter.epFill.style.width=amount+'%'",
        ):
            self.assertIn(text,self.app)
        self.assertIn('/assets/original-ui/battle_hp_bar1.png',self.css)
        self.assertIn('bar.append(epBar)',self.app)
        self.assertNotIn('e.append(epBar)',self.app)
        self.assertIn('.battlefield .unit .hp>.unit-ep',self.css)
        self.assertIn('top:calc(100% + 1px)!important',self.css)
        self.assertNotIn('top:calc(24px + 13px)',self.css)
        self.assertIn('.battlefield .unit.dead .unit-ep{visibility:hidden!important}',self.css)
        self.assertIn("filter:hue-rotate(150deg)",self.css)
        self.assertNotIn("unit-energy-fake",self.app)
        self.assertIn('style.css?v=20261122-sonia-gold-shield-r5',self.html)
        self.assertIn('app.js?v=20261122-skill-click-r10',self.html)

    def test_sonia_idle_attack_skill_motion_is_real_spine(self):
        anim=self.model['animations']
        self.assertEqual(self.model['skeleton']['spine'],'3.6.37')
        self.assertEqual(anim['idle'],anim['battle_idle'])
        self.assertGreater(abs(anim['idle']['bones']['hip']['translate'][2]['y']),20)
        self.assertGreater(max(abs(p['angle']) for p in anim['idle']['bones']['torso']['rotate']),3)
        for name in ('attack','skill'):
            for bone in ('arm_l','arm_r','head'):
                self.assertIn(bone,anim[name]['bones'])
                rotations=anim[name]['bones'][bone]['rotate']
                self.assertGreater(max(abs(p['angle']) for p in rotations),4)
                self.assertEqual(rotations[0]['time'],0)
        self.assertIn('20261122-motion-r1',self.battle)
        self.assertIn("?'battle_idle':",self.battle)
        self.assertIn("setAnimation(1,'blink',false)",self.battle)
        self.assertIn('soniaBlinkTimers.clear()',self.battle)
        self.assertIn('battle-animation.js?v=20261122-sonia-five-daggers-r8',self.html)

    def test_three_passive_vfx_have_real_event_cues(self):
        for phrase in (
            'soniaVisualCue(pos,75800103,[],0,0)',
            'const soniaIsActor=units.get(Number(frame.pos))?.tableId===758001',
            'amount>fighter.ep',
            "soniaEnergyGained=true",
            'soniaFinishedEnemy=true',
            'if(soniaEnergyGained)soniaVisualCue(Number(frame.pos),75800102',
            'if(soniaFinishedEnemy)soniaVisualCue(Number(frame.pos),75800104',
            'if(!skip&&token===battleReplayToken&&battleAnimation===animation)',
            'const soniaFirstActionVfx=new Set()',
            'soniaVisualCue(Number(frame.pos),75800102,soniaTargets,frame.round,0)',
            'soniaVisualCue(Number(frame.pos),75800104,soniaTargets,frame.round,0)',
            'if(soniaOpening.length&&!skip)await new Promise(resolve=>setTimeout(resolve,620/battleSpeed))',
        ):
            self.assertIn(phrase,self.app)
        self.assertIn('soniaNative[Number(skillId)]',self.battle)
        self.assertIn('sonia_chaos_siphon',self.battle)
        self.assertIn('sonia_chaos_guard',self.battle)
        self.assertIn('sonia_chaos_collapse',self.battle)
        self.assertNotIn('state.items',self.app[self.app.index('const soniaCueSeen=new Set()'):self.app.index('for(const frame of report.frames)')])

if __name__=='__main__':
    unittest.main()
