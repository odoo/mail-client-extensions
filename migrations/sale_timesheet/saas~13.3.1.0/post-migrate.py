# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        "UPDATE project_project SET timesheet_product_id = %s WHERE timesheet_product_id IS NULL",
        [util.ref(cr, "sale_timesheet.time_product")],
    )
