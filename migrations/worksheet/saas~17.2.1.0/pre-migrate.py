from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "worksheet_template", "company_id", "int4")
    c_cols = util.get_columns(cr, "worksheet_template", ignore=("id", "company_id"))

    cr.execute(
        """
        WITH first_comp AS (
            SELECT worksheet_template_id as w_id,
                   MIN(res_company_id) as c_id
              FROM res_company_worksheet_template_rel
          GROUP BY worksheet_template_id
        )
        UPDATE worksheet_template w
           SET company_id = first_comp.c_id
          FROM first_comp
         WHERE w.id = first_comp.w_id
        """
    )
    query = util.format_query(
        cr,
        """
        INSERT INTO worksheet_template({cols}, company_id)
             SELECT {wt_cols}, r.res_company_id
               FROM res_company_worksheet_template_rel r
               JOIN worksheet_template wt
                 ON wt.id = r.worksheet_template_id
              WHERE r.res_company_id <> wt.company_id
        """,
        cols=c_cols,
        wt_cols=c_cols.using(alias="wt"),
    )
    cr.execute(query)

    util.adapt_domains(cr, "worksheet.template", "company_ids", "company_id")
    util.remove_field(cr, "worksheet.template", "company_ids")
