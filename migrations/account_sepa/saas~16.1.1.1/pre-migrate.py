# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.change_field_selection_values(
        cr, "account.journal", "sepa_pain_version", {"pain.001.003.03": "pain.001.001.03.de"}
    )
