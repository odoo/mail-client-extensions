# -*- coding: utf-8 -*-
from odoo import models

from odoo.addons.sale_amazon.models import amazon_marketplace  # noqa


class AmazonMarketplace(models.Model):
    _inherit = "amazon.marketplace"
    _module = "sale_amazon"
    _match_uniq = True


def migrate(cr, version):
    pass
