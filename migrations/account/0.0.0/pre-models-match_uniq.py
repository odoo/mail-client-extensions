from odoo import models

from odoo.addons.base.maintenance.migrations import util

try:
    from odoo.addons.account.models import account_tax  # noqa
except ImportError:
    from odoo.addons.account.models import account

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
    _name = "account.tax"
    _inherit = ["account.tax"]
    _module = "account"
    _match_uniq = True


class AccountPaymentMethod(models.Model):
    _name = "account.payment.method"
    _inherit = ["account.payment.method"]
    _module = "account"
    _match_uniq = True


if util.version_gte("16.0"):
    from odoo.addons.account.models import account_report  # noqa

    class AccountReportExpression(models.Model):
        _inherit = "account.report.expression"
        _module = "account"
        _match_uniq = True
        _match_uniq_warning = (
            "Your existing financial report expression {xmlid!r} has been merged with the standard one "
            "that has the same label {label!r}. You should check it to confirm that there is issue."
        )
