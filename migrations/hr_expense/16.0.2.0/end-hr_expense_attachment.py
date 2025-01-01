from odoo.upgrade import util


def migrate(cr, version):
    ia_col = util.get_columns(cr, "ir_attachment", ignore=("id", "res_model", "res_id"))

    cr.execute(
        util.format_query(
            cr,
            """
            INSERT INTO ir_attachment({columns}, res_model, res_id)
                SELECT {he_a_columns}, 'hr.expense.sheet', hes.id
                  FROM ir_attachment he_a
                  JOIN hr_expense he
                    ON he.id = he_a.res_id
                   AND he_a.res_model = 'hr.expense'
                  JOIN hr_expense_sheet hes
                    ON hes.id = he.sheet_id
             LEFT JOIN ir_attachment hes_a
                    ON hes_a.res_id = hes.id
                   AND hes_a.res_model = 'hr.expense.sheet'
                   AND hes_a.checksum = he_a.checksum
                 WHERE hes_a.id IS NULL
            """,
            columns=ia_col,
            he_a_columns=ia_col.using(alias="he_a"),
        )
    )

    cr.execute(
        """
        WITH main_att AS (
            SELECT res_id, min(id) AS id
              FROM ir_attachment
             WHERE res_model = 'hr.expense.sheet'
          GROUP BY res_id
        )
        UPDATE hr_expense_sheet hes
           SET message_main_attachment_id = main_att.id
          FROM main_att
         WHERE hes.message_main_attachment_id IS NULL
           AND main_att.res_id = hes.id
        """
    )
