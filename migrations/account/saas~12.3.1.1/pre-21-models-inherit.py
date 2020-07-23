from odoo import fields, models
from odoo.addons.account.models import account  # noqa


def migrate(cr, version):
    pass


class Account(models.Model):
    _inherit = "account.account"
    _module = "account"

    deprecated = fields.Boolean(compute="_compute_deprecated", search="_search_deprecated", store=False)

    def _compute_deprecated(self):
        for acc in self:
            acc.deprecated = False

    def _search_deprecated(self, operator, value):
        return [(1, operator, 1)]
