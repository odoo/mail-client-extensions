from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "documents_document", "thumbnail_status", "varchar")

    cr.execute(
        """
        UPDATE documents_document doc
           SET thumbnail_status = 'present'
          FROM ir_attachment att
         WHERE att.res_model = 'documents.document'
           AND att.res_id = doc.id
           AND att.res_field = 'thumbnail'
        """
    )

    util.remove_view(cr, "documents.pdf_js_assets")
