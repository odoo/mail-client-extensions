from odoo.upgrade import util


def migrate(cr, version):
    ia_col = util.get_columns(cr, "ir_attachment", ignore=("id", "name", "res_field"))
    cr.execute(
        util.format_query(
            cr,
            """
            INSERT INTO ir_attachment (name, res_field, {columns})
                 SELECT 'image_512', 'image_512', {columns}
                   FROM ir_attachment a
                  WHERE a.name = 'image_128'
                    AND a.res_model IN ('pos.category', 'pos.preset')
                    AND NOT EXISTS (
                            SELECT 1
                              FROM ir_attachment b
                             WHERE b.res_model = a.res_model
                               AND b.res_id = a.res_id
                               AND b.name = 'image_512'
                        )
            """,
            columns=ia_col,
        )
    )
