"""Player-facing internship and exchange error wording, without touching player records."""
import copy
import unittest
from gxb2 import internship, acquisition

class LocalizationBackend(unittest.TestCase):
    def test_internship_missing_resources_is_vietnamese_and_nonmutating(self):
        state={'items':{'2':0,'24':0}}
        initial=copy.deepcopy(state)
        with self.assertRaisesRegex(ValueError, 'Không đủ Kim Cương'):
            internship.pay(state['items'],{'2':3})
        self.assertEqual(state,initial)

    def test_internship_message_for_missing_noncurrency_item(self):
        with self.assertRaisesRegex(ValueError,'Không đủ vật phẩm'):
            internship.pay({'24':0},{'24':1})

    def test_exchange_invalid_parameters_are_localized(self):
        with self.assertRaisesRegex(ValueError,'giá trị không hợp lệ'):
            acquisition.number(None,'Nữ Thần')

    def test_exchange_no_funds_preserves_state(self):
        state={'items':{'19':0}}
        initial=copy.deepcopy(state)
        with self.assertRaisesRegex(ValueError,'Không đủ nguyên liệu hoặc tiền tệ'):
            acquisition.charge(state,{'19':2})
        self.assertEqual(state,initial)

    def test_all_45_quest_names_still_retained_in_original_source(self):
        self.assertEqual(len(internship.DATA['names']),45)
        self.assertEqual(internship.DATA['names']['18'],'Assisting Amazon')
        self.assertEqual(internship.DATA['names']['22'],"Medusa's Threat")

if __name__=='__main__':unittest.main()
