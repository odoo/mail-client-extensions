# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    # many existing customers would have wrong code set for below records of
    # product_unspsc_code table which first needs correction
    cr.execute("""
        UPDATE product_unspsc_code
        SET code = CONCAT('0', code)
        WHERE code IN ('5', '6', '8', '1010101')""")
    # update unspsc_code_id field of product_template and uom_uom tables with same
    # product code that was set in l10n_mx_edi_code_sat_id by Mexican users
    for model in ('product.template', 'uom.uom'):
        cr.execute("""
            UPDATE %s tbl
            SET unspsc_code_id = unspsc.id
            FROM product_unspsc_code unspsc
            JOIN l10n_mx_edi_product_sat_code mx ON unspsc.code = mx.code
            WHERE tbl.l10n_mx_edi_code_sat_id = mx.id
        """ % util.table_of_model(cr, model))
        util.remove_field(cr, model, 'l10n_mx_edi_code_sat_id')

    util.remove_model(cr, "l10n_mx_edi.product.sat.code")
