# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # ===========================================================
    # Task 2567701 : Move Sepa Pain Version
    # ===========================================================
    util.recompute_fields(cr, "account.journal", ["sepa_pain_version"])
