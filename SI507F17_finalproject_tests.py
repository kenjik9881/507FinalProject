import unittest
from SI507F17_finalproject import *

class Test_CryptoClass(unittest.TestCase):
    def setUp(self):
        kenjicoin_dict = {'coin_rank': '1109', 'coin_name': 'Kenjicoin', 'coin_price': '$11124.003', 'coin_marketcap': '$2,589,378,288', 'coin_supply': '15,700,002', 'coin_24hrchange': '10.99%'}

        self.kenjicoin = Cryptocurrency(kenjicoin_dict)

        wigglecoin_dict = {'coin_rank': '1109', 'coin_name': 'Wigglecoin', 'coin_price': '$11124.003', 'coin_marketcap': '$2,589,378,288', 'coin_supply': '15,700,002', 'coin_24hrchange': '-5.99%'}

        self.wigglecoin = Cryptocurrency(wigglecoin_dict)

    def test_coin_rank(self):
        self.assertEqual(self.kenjicoin.coin_rank, 1109)

    def test_coin_rank_type(self):
        self.assertEqual(type(self.kenjicoin.coin_rank), int)

    def test_coin_price_type(self):
        self.assertEqual(type(self.kenjicoin.price), float)

    def test_coin_name(self):
        self.assertEqual(self.kenjicoin.name, 'Kenjicoin')

    def test_supply(self):
        self.assertEqual(self.kenjicoin.supply, '15,700,002')

    def test_supply_type(self):
        self.assertEqual(type(self.kenjicoin.supply), str)

    def test_coin_marketmap_type(self):
        self.assertNotEqual(type(self.kenjicoin.marketcap), str)

    def test_24_hr_change(self):
        self.assertEqual(self.kenjicoin.percent_change, 10.99)

    def test_get_old_price(self):
        self.assertEqual(self.kenjicoin.get_old_price(), 10022.52)

    def test_get_old_price_negative_value(self):
        self.assertEqual(self.wigglecoin.get_old_price(), 11832.78)

    def test_get_item(self):
        self.assertEqual(self.kenjicoin['name'],'Kenjicoin')

    def tearDown(self):
        pass

class Test_Exchange(unittest.TestCase):
    def setUp(self):
        myexchange = {"Name of coin": "Bitcoin", "exchange_name": "Goldenchild Exchange", "exchange_price": "$12003.052"}

        self.goldenexchange = Exchange(myexchange)

    def test_exchange_name(self):
        self.assertEqual(self.goldenexchange.exchange_name, "Goldenchild Exchange")

    def test_exchange_price(self):
        self.assertEqual(self.goldenexchange.exchange_price, 12003.05)

    def test_exchange_coin_name(self):
        self.assertEqual(self.goldenexchange.name_of_coin, "Bitcoin")

    def test_price_type(self):
        self.assertEqual(type(self.goldenexchange.exchange_price), float)

    def tearDown(self):
        pass







if __name__ == "__main__":
    unittest.main(verbosity=2)
