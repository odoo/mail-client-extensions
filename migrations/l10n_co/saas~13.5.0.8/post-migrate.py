# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    cr.execute('''UPDATE res_partner rp
                  SET l10n_latam_identification_type_id = ltype.id
                  FROM l10n_latam_identification_type ltype
                  WHERE ltype.l10n_co_document_code = rp.l10n_co_document_type
    ''')
    util.remove_field(cr, 'res.partner', 'l10n_co_document_type')
