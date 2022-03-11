# -*- coding: utf-8 -*-

from collections import namedtuple

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~15.5")
class TestZipConversion(UpgradeCase):
    def prepare(self):
        product_delivery_normal = self.env["product.product"].create(
            {
                "name": "Normal Delivery Charges",
                "type": "service",
                "list_price": 10.0,
                "categ_id": self.env.ref("delivery.product_category_deliveries").id,
            }
        )
        # carrier_names correspond to what is being tested
        # num_prefixes is used for asserts so we can have complicated use cases without comparing large lists
        # For posterity, expected prefixes by carrier_name are:
        #
        # test_basic: ['1001', '1002', '1003', '1004', '1005', '1006', '1007', '1008', '1009', '101', '102',
        #              '103', '104', '105', '106', '107', '108', '109', '11', '12', '13', '14', '15', '16',
        #              '17', '18', '19', '200', '2010']
        # test_separators: same as test_basic, but with a '-' in prefix[2] if 3+ chars without separators and a
        #                  space in prefix[4] if 4+ chars without separators
        # test_mismatching_separators: doesn't convert, displays message warning
        # test_basic_letters: ['100A', '100B', '100C', '100D', '100E', '100F', '100G', '100H', '100I', '100J',
        #                      '100K', '100L', '100M', '100N', '100O', '100P', '100Q', '100R', '100S', '100T',
        #                      '100U', '100V', '100W', '100X', '100Y', '100Z', '101', '102', '103', '104',
        #                      '105', '106', '107', '108', '109', '10A', '10B', '10C', '10D', '10E', '10F',
        #                      '10G', '10H', '10I', '10J', '10K', '10L', '10M', '10N', '10O', '10P', '10Q',
        #                      '10R', '10S', '10T', '10U', '10V', '10W', '10X', '10Y', '10Z', '11', '12', '13',
        #                      '14', '15', '16', '17', '18', '19', '1A', '1B', '1C', '1D', '1E', '1F', '1G',
        #                      '1H', '1I', '1J', '1K', '1L', '1M', '1N', '1O', '1P', '1Q', '1R', '1S', '1T',
        #                      '1U', '1V', '1W', '1X', '1Y', '1Z', '200', '2010', '2011', '2012', '2013',
        #                      '2014', '2015', '2016', '2017', '2018', '2019', '201A', '201B']
        # test_letters_w_separators: same as test_basic_letters, but with a '-' in prefix[2] if 3+ chars
        # test_same: ['100']
        # test_from_gt_to: doesn't convert, NO warning message since no prefix == existing behavior
        # test_len_mismatch:doesn't convert, displays message warning
        # test_bad_chars: doesn't convert, displays message warning
        # test_bad_chars_w_separators: doesn't convert, displays message warning
        DataPoint = namedtuple("DataPoint", ["carrier_name", "zip_from", "zip_to", "num_prefixes"])
        data = [
            DataPoint("test_basic", "1001", "2010", 29),
            DataPoint("test_separators", "10-0 1", "20-1 0", 29),
            DataPoint("test_mismatching_separators", "10-01", "201-0", 0),
            DataPoint("test_basic_letters", "100a", "201B", 109),
            DataPoint("test_letters_w_separators", "10-0a", "20-1B", 109),
            DataPoint("test_same", "100", "100", 1),
            DataPoint("test_from_gt_to", "2001", "1002", 0),
            DataPoint("test_len_mismatch", "100", "1000", 0),
            DataPoint("test_bad_chars", "&é", "20", 0),
            DataPoint("test_bad_chars_w_separators", "&-é", "2-0", 0),
        ]
        carrier_ids = []
        for data_point in data:
            carrier = self.env["delivery.carrier"].create(
                {
                    "name": data_point.carrier_name,
                    "zip_from": data_point.zip_from,
                    "zip_to": data_point.zip_to,
                    "product_id": product_delivery_normal.id,
                }
            )
            carrier_ids.append((carrier.id, data_point.num_prefixes))
        return {"carrier_ids": carrier_ids}

    def check(self, init):
        for carrier_id, num_prefixes in init["carrier_ids"]:
            carrier = self.env["delivery.carrier"].browse(carrier_id)
            self.assertEqual(len(carrier.zip_prefix_ids), num_prefixes, "%s didn't correctly convert" % carrier.name)
