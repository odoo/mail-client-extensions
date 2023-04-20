from odoo.upgrade import util


def migrate(cr, version):
    if not util.module_installed(cr, "account_payment_invoice_online_payment_patch"):
        # if bugfix module allowing to disable portal payments was not
        # installed, customer expect online payment to be enabled; so we
        # force the creation of the system parameter.
        cr.execute(
            """
            INSERT
              INTO ir_config_parameter(key, value)
            VALUES ('account_payment.enable_portal_payment', 'True')
                ON CONFLICT (key)
                DO NOTHING
            """
        )
