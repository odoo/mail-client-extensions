# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        "ALTER TABLE account_move ALTER auto_post TYPE varchar USING CASE WHEN auto_post=TRUE THEN 'at_date' ELSE 'no' END"
    )
    util.create_column(cr, "account_move", "auto_post_until", "date")
