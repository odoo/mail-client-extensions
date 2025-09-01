from odoo import models

from odoo.addons.account_ponto.models import ponto as _ignore  # noqa

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    pass


# avoid fetching/removing data from the provider during the upgrade
if util.version_gte("12.0"):

    class PontoProviderAccount(models.Model):
        _name = "account.online.provider"
        _inherit = ["account.online.provider"]
        _module = "account_ponto"

        def _ponto_fetch(self, method, url, params, data):
            pass
