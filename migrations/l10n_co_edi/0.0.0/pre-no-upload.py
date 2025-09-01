# -*- coding: utf-8 -*-
from odoo import models

from odoo.addons.l10n_co_edi.models import account_invoice as _ignore  # noqa

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    pass


class Invoice(models.Model):
    _name = "account.move" if util.version_gte("saas~12.4") else "account.invoice"
    _inherit = ["account.move"] if util.version_gte("saas~12.4") else ["account.invoice"]
    _module = "l10n_co_edi"

    def _l10n_co_edi_is_l10n_co_edi_required(self):
        return False
