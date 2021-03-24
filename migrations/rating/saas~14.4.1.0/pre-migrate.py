# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.change_field_selection_values(
        cr,
        "rating.rating",
        "rating_text",
        {
            "highly_dissatisfied": "ko",
            "not_satisfied": "ok",
            "satisfied": "top",
            "no_rating": "none",
        },
    )
