from odoo.upgrade import util


def migrate(cr, version):
    env = util.env(cr)
    CoA = env["account.chart.template"]
    for company in env["res.company"].search([("chart_template", "=", "ph")], order="parent_path"):
        CoA.try_loading("ph", company=company, install_demo=False)
