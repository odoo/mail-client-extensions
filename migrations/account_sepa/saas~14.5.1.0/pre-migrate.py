# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # ===========================================================
    # Task 2567701 : Move Sepa Pain Version
    # ===========================================================
    util.remove_field(cr, "res.company", "sepa_pain_version")
    util.remove_field(cr, "res.config.settings", "sepa_pain_version")
    util.create_column(cr, "account_journal", "sepa_pain_version", "varchar")
