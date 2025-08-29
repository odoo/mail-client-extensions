from odoo.upgrade import util


def migrate(cr, version):
    cr.execute("UPDATE res_company SET chart_template = 'ca_2023' WHERE chart_template = 'ca' RETURNING id")
    ids = [r[0] for r in cr.fetchall()]
    if ids:
        env = util.env(cr)
        companies = env["res.company"].search([("id", "in", ids)], order="parent_path")
        companies.invalidate_recordset()  # necessary due to the update query above!
        for company in companies:
            env["account.chart.template"].try_loading("ca_2023", company)
