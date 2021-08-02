# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.convert_field_to_property(
        cr, "product.template", "worksheet_template_id", type="many2one", target_model="worksheet.template"
    )
