# -*- coding: utf-8 -*-
from odoo import models
from odoo.addons.account.models import account  # noqa


def migrate(cr, version):
    pass


class Tax(models.Model):
    _inherit = "account.tax"
    _module = "account"
    _match_uniq = True
