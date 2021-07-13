# -*- coding: utf-8 -*-
from odoo import models

from odoo.addons.payment.models import account_journal  # noqa


def migrate(cr, version):
    pass


class Journal(models.Model):
    _inherit = "account.journal"
    _module = "payment"

    def _check_inbound_payment_method_line_ids(self):
        pass
