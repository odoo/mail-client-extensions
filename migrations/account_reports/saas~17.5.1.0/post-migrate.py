from odoo.upgrade import util


def migrate(cr, version):
    generic_tax_report_id = util.ref(cr, "account.generic_tax_report")
    util.explode_execute(
        cr,
        cr.mogrify(
            """
        WITH _report AS (
            SELECT MIN(id) as id, country_id
              FROM account_report
             WHERE availability_condition = 'country'
               AND root_report_id = %(generic_tax_report_id)s
          GROUP BY country_id
        )
        UPDATE account_move am
           SET tax_closing_report_id = COALESCE(r.id, %(generic_tax_report_id)s)
          FROM account_move am1
          JOIN res_company c
            ON c.id = am1.company_id
     LEFT JOIN account_fiscal_position vat_fpos
            ON am1.fiscal_position_id = vat_fpos.id AND vat_fpos.foreign_vat IS NOT NULL
     LEFT JOIN _report r
            ON r.country_id = COALESCE(vat_fpos.country_id, c.account_fiscal_country_id)
         WHERE am.id = am1.id
           AND am.tax_closing_end_date IS NOT NULL
			""",
            {"generic_tax_report_id": generic_tax_report_id},
        ).decode(),
        table="account_move",
        alias="am",
    )
    util.remove_field(cr, "account.move", "tax_closing_end_date")
    util.remove_field(cr, "account.move", "tax_report_control_error")
