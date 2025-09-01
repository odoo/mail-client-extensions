from odoo import api, models

from odoo.addons.account_yodlee.models import yodlee as _ignore  # noqa

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    pass


# avoid fetching/removing data from the provider during the upgrade
if util.version_gte("13.0"):

    class YodleeProviderAccount(models.Model):
        _name = "account.online.provider"
        _inherit = ["account.online.provider"]
        _module = "account_yodlee"

        def yodlee_fetch(self, url, params, data, type_request="POST"):
            pass


else:

    class YodleeProviderAccount(models.Model):
        _name = "account.online.provider"
        _inherit = ["account.online.provider"]
        _module = "account_yodlee"

        @api.multi
        def yodlee_fetch(self, url, params, data, type_request="POST"):
            pass
