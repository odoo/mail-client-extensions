# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.rename_model(
        cr,
        "report.quality_worksheet.worksheet_custom",
        "report.quality_control_worksheet.worksheet_custom",
        rename_table=False,
    )
