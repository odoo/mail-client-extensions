from odoo import models

from odoo.addons.account.models import chart_template  # noqa

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    pass


if util.version_gte("saas~16.4"):

    class ChartTemplate(models.AbstractModel):
        _name = "account.chart.template"
        _inherit = ["account.chart.template"]
        _module = "account"

        def _load_data(self, data, *args, **kwargs):
            if set(data.keys()) == {"res.company"}:
                needed_account_xmlids = {
                    xmlid
                    for (c_id, vals) in data["res.company"].items()
                    for (field_name, xmlid) in vals.items()
                    if field_name in ("deferred_expense_account_id", "deferred_revenue_account_id")
                    and xmlid
                    and not self.ref(xmlid, raise_if_not_found=False)
                }
                if needed_account_xmlids:
                    chart_code = self.env.company.chart_template
                    account_data = self._get_chart_template_data(chart_code)
                    if "account.account" in account_data:
                        data["account.account"] = {
                            account: account_data["account.account"][account] for account in needed_account_xmlids
                        }
            return super()._load_data(data, *args, **kwargs)
