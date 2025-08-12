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

    util.explode_execute(
        cr,
        """
        UPDATE documents_document
           SET lock_uid = NULL
         WHERE type = 'folder'
           AND lock_uid IS NOT NULL
        """,
        table="documents_document",
    )

    util.remove_view(cr, "documents.mail_template_document_share")
