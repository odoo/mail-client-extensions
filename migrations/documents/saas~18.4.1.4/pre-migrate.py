from odoo.upgrade import util


def migrate(cr, version):
    util.explode_execute(
        cr,
        """
        UPDATE documents_document
           SET res_model = NULL,
               res_id = NULL
         WHERE res_model = 'documents.document'
        """,
        table="documents_document",
    )
