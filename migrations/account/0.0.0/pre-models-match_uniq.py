# -*- coding: utf-8 -*-
from odoo import models

try:
    from odoo.addons.account.models import account_tax  # noqa
except ImportError:
    from odoo.addons.account.models import account  # noqa

try:
    from odoo.addons.account.models import account_payment_method  # noqa
except ImportError:
    try:
        from odoo.addons.account.models import account_payment  # noqa
    except ImportError:
        from odoo.addons.account.models import account  # noqa


def migrate(cr, version):
    pass


class Tax(models.Model):
    _inherit = "account.tax"
    _module = "account"
    _match_uniq = True


class AccountPaymentMethod(models.Model):
    _inherit = "account.payment.method"
    _module = "account"
    _match_uniq = True
