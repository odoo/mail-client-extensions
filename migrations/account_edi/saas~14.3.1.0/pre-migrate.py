# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):

    # ===========================================================
    # merge account_edi_extended in account_edi (PR: 65745 & 16226)
    # ===========================================================

    util.create_column(cr, 'account_edi_document', 'blocking_level', 'varchar')
    cr.execute("""UPDATE account_edi_document
                     SET blocking_level = 'warning'
                   WHERE blocking_level IS NULL
                     AND error IS NOT NULL
    """)
    util.remove_view(cr, 'account_edi.view_tree_account_edi_document_inherit')
