from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "payment_demo.payment_method_test")

    cr.execute(
        """
            UPDATE payment_provider
               SET code = 'demo'
             WHERE code = 'test'
        """
    )
    util.rename_field(cr, "payment.token", "test_simulated_state", "demo_simulated_state")
    util.rename_xmlid(
        cr,
        "payment_demo.payment_transaction_form_inherit_payment_test",
        "payment_demo.payment_transaction_form",
    )
