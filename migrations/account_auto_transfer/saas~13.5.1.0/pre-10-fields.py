# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # New fields introduced by PR 10890
    util.create_m2m(cr, "account_transfer_model_line_res_partner_rel", "account_transfer_model_line", "res_partner")
    util.create_column(cr, "account_transfer_model_line", "sequence", "int4")
