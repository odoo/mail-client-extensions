from odoo.upgrade import util


def migrate(cr, version):
    util.convert_field_to_translatable(cr, "account.tax.group", "preceding_subtotal")
    cr.execute("""
        DELETE
          FROM ir_sequence s
         USING account_journal j
         WHERE s.id = j.secure_sequence_id
    """)
    util.remove_field(cr, "account.journal", "secure_sequence_id")
    util.remove_field(cr, "account.group", "parent_path")
