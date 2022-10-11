from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(
        cr,
        "payment_demo.payment_method_test",
        "payment_demo.payment_method_demo",
    )
    util.update_record_from_xml(cr, "payment_demo.payment_method_demo")

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
