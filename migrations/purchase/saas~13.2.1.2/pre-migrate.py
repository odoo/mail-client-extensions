# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "purchase.access_account_move_purchase")
    util.remove_record(cr, "purchase.access_account_move_purchase_manager")
