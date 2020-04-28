# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_model(cr, "test_marketing_automation.test.simple", drop_table=True)
