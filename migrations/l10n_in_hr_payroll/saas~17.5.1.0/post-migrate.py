from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
          UPDATE ir_sequence
             SET company_id = NULL
           WHERE id = %s
        """,
        [util.ref(cr, "l10n_in_hr_payroll.seq_payment_advice")],
    )
