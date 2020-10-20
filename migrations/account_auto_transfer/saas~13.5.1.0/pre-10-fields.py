# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_m2m(cr, "account_transfer_model_line_res_partner_rel", "account_transfer_model_line", "res_partner")
    util.create_column(cr, "account_transfer_model_line", "sequence", "int4")
    cr.execute("UPDATE account_transfer_model_line SET sequence = id")
