from odoo.upgrade import util


def migrate(cr, version):
    # since l10n_in_withholding has been merged into l10n_in we need to ensure
    # that taxes are loaded in case the module was not installed
    if not util.ENVIRON["l10n_in_withholding"]:
        env = util.env(cr)
        for company in env["res.company"].search([("chart_template", "=", "in")], order="parent_path"):
            env["account.chart.template"].try_loading("in", company)
