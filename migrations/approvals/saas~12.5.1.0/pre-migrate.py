# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, 'approval_category', 'active', 'boolean')
    util.rename_field(cr, 'approval.category', 'requirer_document', 'requirer_document_old')
    util.create_column(cr, 'approval_category', 'requirer_document', 'varchar')
    cr.execute("""
        UPDATE approval_category
           SET active=TRUE,
               requirer_document=CASE
                                    WHEN requirer_document_old THEN 'required'
                                    ELSE 'optional'
                                 END
    """)
    util.remove_field(cr, 'approval.category', 'requirer_document_old')
    util.remove_field(cr, 'approval.request', 'requirer_document')
