from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "payment_sepa_direct_debit.mail_template_sepa_notify_debit")
    util.remove_field(cr, "account.move", "sdd_mandate_scheme")
