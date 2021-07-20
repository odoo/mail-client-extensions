# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "utm_campaign", "ab_testing_sms_winner_selection", "varchar", default="clicks_ratio")
