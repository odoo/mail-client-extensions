from odoo import models

from odoo.addons.account.models import account_payment_method as _ignore  # noqa

from odoo.upgrade import util


class AccountPaymentMethod(models.Model):
    _inherit = "account.payment.method"
    _module = "account_iso20022"

    def _auto_link_payment_methods(self, payment_methods, methods_info):
        return payment_methods


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_field(cr, "res.company", *eb("{sepa,iso20022}_initiating_party_name"))
    util.rename_field(cr, "res.config.settings", *eb("{sepa,iso20022}_initiating_party_name"))
    util.rename_field(cr, "res.company", *eb("{sepa,iso20022}_orgid_id"))
    util.rename_field(cr, "res.config.settings", *eb("{sepa,iso20022}_orgid_id"))
    util.rename_field(cr, "res.company", *eb("{sepa,iso20022}_orgid_issr"))
    util.rename_field(cr, "res.config.settings", *eb("{sepa,iso20022}_orgid_issr"))
    util.rename_field(cr, "account.batch.payment", *eb("{sct,iso20022}_batch_booking"))
    util.rename_field(cr, "account.payment", *eb("{sepa,iso20022}_uetr"))
    util.rename_field(cr, "res.users", *eb("{account_sepa,iso20022}_lei"))
    util.rename_field(cr, "res.partner", *eb("{account_sepa,iso20022}_lei"))
    util.rename_field(cr, "res.company", *eb("{account_sepa,iso20022}_lei"))

    util.remove_field(cr, "account.batch.payment", "sct_generic")
