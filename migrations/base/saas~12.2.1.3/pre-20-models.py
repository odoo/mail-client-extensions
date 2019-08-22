# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute("ALTER TABLE res_lang ALTER COLUMN week_start TYPE varchar")

    if util.module_installed(cr, "point_of_sale"):
        # in previous versions, field was declared in both modules
        # free xmlid to avoid duplicate
        cr.execute("""
            DELETE FROM ir_model_data
                  WHERE module = 'point_of_sale'
                    AND name = 'field_res_partner__barcode'
        """)
        util.move_field_to_module(cr, "res.partner", "barcode", "base", "point_of_sale")
    else:
        util.remove_field(cr, "res.partner", "barcode")

    util.force_noupdate(cr, "base.view_partner_form", False)
