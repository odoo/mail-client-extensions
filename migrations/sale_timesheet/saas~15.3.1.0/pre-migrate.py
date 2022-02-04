# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.change_field_selection_values(
        cr,
        "product.template",
        "service_policy",
        {
            "ordered_timesheet": "ordered_prepaid",
        },
    )
