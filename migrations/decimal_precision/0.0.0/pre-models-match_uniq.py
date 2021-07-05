from odoo import models

from odoo.addons.decimal_precision.models import decimal_precision  # noqa


def migrate(cr, version):
    pass


class Tags(models.Model):
    _inherit = "decimal.precision"
    _module = "decimal_precision"
    _match_uniq = True
