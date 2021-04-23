# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.change_field_selection_values(
        cr,
        "mailing.mailing",
        "reply_to_mode",
        {"email": "new", "thread": "update"},
    )
