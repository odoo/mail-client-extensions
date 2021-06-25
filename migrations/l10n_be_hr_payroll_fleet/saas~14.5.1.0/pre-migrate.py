# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "hr_contract", "new_bike", "boolean")

    cr.execute(
        """
        UPDATE hr_contract
           SET new_bike = 't'
           WHERE new_bike_model_id IS NOT NULL
    """
    )
