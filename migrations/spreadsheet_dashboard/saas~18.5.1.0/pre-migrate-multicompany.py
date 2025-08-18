from odoo.upgrade import util


def migrate(cr, version):
    util.create_m2m(cr, "res_company_spreadsheet_dashboard_rel", "spreadsheet_dashboard", "res_company")
    cr.execute(
        """
        INSERT INTO res_company_spreadsheet_dashboard_rel (spreadsheet_dashboard_id, res_company_id)
        SELECT id, company_id
          FROM spreadsheet_dashboard
         WHERE company_id IS NOT NULL
    """,
    )
    util.remove_column(cr, "spreadsheet_dashboard", "company_id")
    util.rename_field(cr, "spreadsheet.dashboard", "company_id", "company_ids")
