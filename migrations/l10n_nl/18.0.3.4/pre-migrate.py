from odoo import models

from odoo.addons.account.models import chart_template  # noqa


class AccountChartTemplate(models.AbstractModel):
    _inherit = ["account.chart.template"]
    _module = "l10n_nl"

    def try_loading(self, template_code, company, install_demo=False, force_create=True):
        return super().try_loading(
            template_code, company, install_demo=install_demo, force_create=template_code == "nl" or force_create
        )


def migrate(cr, version):
    pass
