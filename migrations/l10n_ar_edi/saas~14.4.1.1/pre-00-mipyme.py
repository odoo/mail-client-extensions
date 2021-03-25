# -*- coding: utf-8 -*-

from odoo.upgrade import util

def migrate(cr, version):
    """ We thought people would always use the same setting for mipyme in AR, but
    it seems to be less and less the case, so before, we added a system param,
    but now it can be different for every invoice with a default on the company"""
    util.create_column(cr, "res_company", "l10n_ar_fce_transmission_type", "varchar")
    util.create_column(cr, "account_move", "l10n_ar_fce_transmission_type", "varchar")
    cr.execute("""WITH t AS (SELECT value
                               FROM ir_config_parameter
                              WHERE key='l10n_ar_edi.fce_transmission')
                  UPDATE res_company
                     SET l10n_ar_fce_transmission_type = t.value
                    FROM t
                    """)
    cr.execute("""
        WITH t AS (SELECT value
                     FROM ir_config_parameter
                    WHERE key='l10n_ar_edi.fce_transmission')
        UPDATE account_move
           SET l10n_ar_fce_transmission_type = t.value
          FROM l10n_latam_document_type doc,
               t
         WHERE account_move.l10n_latam_document_type_id = doc.id
           AND doc.code in ('201', '206', '211', '202', '203', '207', '208', '212', '213')
    """)
    cr.execute("DELETE FROM ir_config_parameter WHERE key='l10n_ar_edi.fce_transmission'")
