from odoo.upgrade import util


def migrate(cr, version):
    cr.execute("SELECT id FROM res_company WHERE chart_template = 'be_comp' ORDER BY parent_path")
    for (company_id,) in cr.fetchall():
        util.rename_xmlid(
            cr, *util.expand_braces(f"account.{company_id}_{{virements_internes_template,internal_transfer_reco}}")
        )
