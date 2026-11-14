import json
import unittest

from gxb2 import live_service


class PvPPublicPayloadTests(unittest.TestCase):
    def test_pre_finish_payload_hides_internal_rng_and_snapshots(self):
        row={
            "id":"PVP-TEST","mode":"arena","server_id":"S1","server_a":"S1","server_b":"S1",
            "player_a":"A","player_b":"B","name_a":"A","name_b":"B","power_a":1,"power_b":2,
            "status":"active","winner_uid":"","created_at":1,"resolved_at":0,
            "seed":12345,"snapshot_a":json.dumps({"secret":"a"}),
            "snapshot_b":json.dumps({"secret":"b"}),"battle_report":json.dumps({"frames":[1]}),
            "rating_delta_a":0,"rating_delta_b":0,
        }
        out=live_service._public_pvp_match(row)
        self.assertNotIn("seed",out)
        self.assertNotIn("snapshot_a",out)
        self.assertNotIn("snapshot_b",out)
        self.assertNotIn("battle_report",out)

    def test_finished_payload_exposes_result_but_never_seed(self):
        row={
            "id":"PVP-TEST","mode":"arena","server_id":"S1","server_a":"S1","server_b":"S1",
            "player_a":"A","player_b":"B","name_a":"A","name_b":"B","power_a":1,"power_b":2,
            "status":"finished","winner_uid":"A","created_at":1,"resolved_at":2,
            "seed":12345,"snapshot_a":json.dumps({"team":[1]}),
            "snapshot_b":json.dumps({"team":[2]}),"battle_report":json.dumps({"isWin":1,"frames":[]}),
            "rating_delta_a":16,"rating_delta_b":-16,
        }
        out=live_service._public_pvp_match(row,include_result=True)
        self.assertNotIn("seed",out)
        self.assertEqual(out["battle_report"]["isWin"],1)
        self.assertEqual(out["snapshot_a"]["team"],[1])


if __name__=="__main__":
    unittest.main()
