# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "utm_campaign", "ab_testing_sms_winner_selection", "varchar", default="clicks_ratio")
