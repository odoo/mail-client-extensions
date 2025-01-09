from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "account.product_template_view_tree")

    cr.execute("""
      UPDATE ir_sequence
         SET prefix = 'GROUP/%(year)s/'
        FROM res_company c
       WHERE ir_sequence.prefix = 'BATCH/%(year)s/'
         AND c.batch_payment_sequence_id = ir_sequence.id
    """)
