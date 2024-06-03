from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "account.batch.payment", "sct_warning")
    util.create_column(cr, "account_batch_payment", "sct_batch_booking", "boolean")

    ICP = util.env(cr)["ir.config_parameter"]
    batch_booking = util.str2bool(ICP.get_param("account_sepa.batch_payment_batch_booking"), default=False)
    cr.execute("UPDATE account_batch_payment SET sct_batch_booking = %s", [batch_booking])
    ICP.set_param("account_sepa.batch_payment_batch_booking", None)
