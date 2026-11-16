"""Protect the owner's profile and original player EXP thresholds."""
import tempfile
import unittest
from pathlib import Path
from gxb2.engine import Engine, GameError, TABLES, super_gm_player_exp_update


class PlayerExpPlanTest(unittest.TestCase):
    def test_amount_uses_original_level_thresholds_and_cap(self):
        sample={'items':{'3':int(TABLES['exp_player']['80']['all_exp']),'2':17},
                'profile':{'avatar':'head_1001'}}
        original=sample['items']['3']
        self.assertEqual(super_gm_player_exp_update(sample,'add',1000000),1000000)
        self.assertEqual(sample['items']['3'],original+1000000)
        self.assertEqual(sample['items']['2'],17)
        max_exp=int(TABLES['exp_player']['400']['all_exp'])
        self.assertEqual(super_gm_player_exp_update(sample,'add',10**12),max_exp-original-1000000)
        self.assertEqual(sample['items']['3'],max_exp)

    def test_target_level_cannot_decrease_exp(self):
        threshold=int(TABLES['exp_player']['81']['all_exp'])
        sample={'items':{'3':threshold}}
        result=super_gm_player_exp_update(sample,'level',82)
        self.assertEqual(result,int(TABLES['exp_player']['82']['all_exp'])-threshold)
        with self.assertRaisesRegex(GameError,'đạt hoặc vượt'):
            super_gm_player_exp_update(sample,'level',81)
        with self.assertRaisesRegex(GameError,'đạt hoặc vượt'):
            super_gm_player_exp_update(sample,'level',82)

    def test_invalid_inputs_do_not_mutate_profile(self):
        for mode,value in [('add',0),('add',-1),('add',False),
                           ('add','1000'),('add',1e9),('add',10**12+1),
                           ('level',0),('level',401),('level','400'),
                           ('reset',100)]:
            sample={'items':{'3':1000,'2':9}}
            with self.assertRaises(GameError,msg=str((mode,value))):
                super_gm_player_exp_update(sample,mode,value)
            self.assertEqual(sample['items'],{'3':1000,'2':9})

    def test_server_developer_action_requires_super_gm_and_only_saves_player_exp(self):
        with tempfile.TemporaryDirectory() as temp:
            game=Engine(Path(temp)/'profile.sqlite3')
            try:
                before=game.snapshot()
                with self.assertRaisesRegex(GameError,'SUPER GM'):
                    game.developer_action({'action':'player_exp','mode':'add','value':5000})
                self.assertEqual(game.snapshot()['items']['3'],before['items']['3'])
                result=game.developer_action({'action':'player_exp','mode':'add','value':5000},super_gm=True)
                self.assertEqual(result['items']['3'],before['items']['3']+5000)
                self.assertEqual(result['items']['2'],before['items']['2'])
                self.assertEqual(result['partners'],before['partners'])
                self.assertEqual(game.snapshot()['items']['3'],result['items']['3'])
            finally:
                game.close()


if __name__=='__main__':
    unittest.main()
