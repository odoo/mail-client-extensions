# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    cr.execute("SELECT id FROM account_move WHERE state IN ('draft', 'cancel')")
    line_ids = [id[0] for id in cr.fetchall()]
    util.recompute_fields(cr, "account.move", ["amount_residual", "amount_residual_signed"], ids=line_ids)
