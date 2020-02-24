# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):

    # Removed fields
    removed_fields = {
        "hr.contract": ["country_code", "transport_employer_cost", "ucm_insurance", "transport_mode_others"],
    }
    for model, fields in removed_fields.items():
        for field in fields:
            util.remove_field(cr, model, field)
