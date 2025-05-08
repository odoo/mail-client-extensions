from odoo.upgrade import util


def migrate(cr, version):
    cr.execute("""
        UPDATE ir_attachment att
           SET res_field = 'response_file'
          FROM l10n_uk_hmrc_transaction transaction
         WHERE att.id = transaction.response_attachment_id
    """)

    util.create_column(cr, "l10n_uk_hmrc_transaction", "response_filename", "varchar")
    cr.execute("""
        UPDATE l10n_uk_hmrc_transaction transaction
           SET response_filename = att.name
          FROM ir_attachment att
         WHERE transaction.response_attachment_id = att.id
    """)
    util.remove_field(cr, "l10n_uk.hmrc.transaction", "response_attachment_id")
