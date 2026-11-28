"""Original stacked Anima inventory must only convert after a validated request."""
import copy
import random
import unittest
from gxb2 import souls

class ReceiveInventoryGear(unittest.TestCase):
    def setUp(self):
        self.stone = int(sorted(souls.E2)[-1])
        self.art = int(sorted(souls.E1)[0])
        self.state = {'items':{str(self.stone):18,str(self.art):2},'partners':[]}
        souls.store(self.state)
        self.rng = random.Random(1024)

    def receive(self, item_id, count):
        return souls.action(self.state,{'action':'receive_inventory_gear','item_id':item_id,'count':count},self.rng)

    def test_single_stone_keeps_type_level_and_count(self):
        response = self.receive(self.stone,1)
        self.assertEqual(len(response['got']),1)
        self.assertEqual(self.state['items'][str(self.stone)],17)
        record=self.state['souls']['items'][str(response['got'][0])]
        self.assertEqual(record['kind'],2)
        self.assertEqual(record['table_id'],self.stone)
        self.assertEqual(record['lv'],0)
        self.assertEqual(record['owner'],0)

    def test_ten_stones_are_ten_unique_records(self):
        response=self.receive(self.stone,10)
        self.assertEqual(len(response['got']),10)
        self.assertEqual(len(set(response['got'])),10)
        self.assertEqual(self.state['items'][str(self.stone)],8)

    def test_artifact_is_supported(self):
        response=self.receive(self.art,1)
        self.assertEqual(self.state['items'][str(self.art)],1)
        self.assertEqual(self.state['souls']['items'][str(response['got'][0])]['kind'],1)

    def test_invalid_requests_do_not_debit_stock(self):
        for data in [(0,1),(self.stone,0),(self.stone,-1),(self.stone,11),(self.stone,19),
                     ('abc',1),(self.stone,'invalid'),(5200009,1)]:
            before=copy.deepcopy(self.state)
            with self.assertRaises(souls.SoulError):self.receive(*data)
            self.assertEqual(self.state,before)

    def test_capacity_rejects_before_debit(self):
        self.state['souls']={'items':{str(i):{} for i in range(souls.LIMIT)},'next':souls.LIMIT+1}
        before=copy.deepcopy(self.state['items'])
        with self.assertRaisesRegex(souls.SoulError,'đủ chỗ'):self.receive(self.stone,1)
        self.assertEqual(self.state['items'],before)

if __name__=='__main__':unittest.main()
