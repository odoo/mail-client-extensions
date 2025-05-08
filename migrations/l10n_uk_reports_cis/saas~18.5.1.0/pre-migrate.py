from odoo.upgrade import util


def migrate(cr, version):
    cr.execute("""
        UPDATE ir_attachment att
           SET res_field = 'document_file'
          FROM l10n_uk_hmrc_transaction transaction
         WHERE att.id = transaction.document_attachment_id
    """)

    util.create_column(cr, "l10n_uk_hmrc_transaction", "document_filename", "varchar")
    cr.execute("""
        UPDATE l10n_uk_hmrc_transaction transaction
           SET document_filename = att.name
          FROM ir_attachment att
         WHERE transaction.document_attachment_id = att.id
    """)
    util.remove_field(cr, "l10n_uk.hmrc.transaction", "document_attachment_id")
