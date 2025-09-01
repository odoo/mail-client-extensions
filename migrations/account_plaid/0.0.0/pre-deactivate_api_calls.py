from odoo import api, models

from odoo.addons.account_plaid.models import plaid as _ignore  # noqa

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    pass


# avoid fetching/removing data from the provider during the upgrade
if util.version_gte("12.0"):

    class PlaidProviderAccount(models.Model):
        _name = "account.online.provider"
        _inherit = ["account.online.provider"]
        _module = "account_plaid"

        def plaid_fetch(self, url, data):
            pass


else:

    class PlaidProviderAccount(models.Model):
        _name = "account.online.provider"
        _inherit = ["account.online.provider"]
        _module = "account_plaid"

        @api.multi
        def plaid_fetch(self, url, params, data, type_request="POST"):
            pass
