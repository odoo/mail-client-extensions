from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        UPDATE ir_attachment att
           SET res_field = 'l10n_ke_oscu_attachment_file',
               res_model = 'stock.move',
               res_id = stock_move.id
          FROM stock_move
         WHERE att.id = stock_move.l10n_ke_oscu_attachment_id
           AND att.res_model is NULL
           AND att.res_id is NULL
        """
    )

    cols = util.get_columns(cr, "ir_attachment", ignore=("id", "res_id", "res_model", "res_field"))
    query = util.format_query(
        cr,
        """
        INSERT INTO ir_attachment (
            res_id,
            res_model,
            res_field,
            {columns}
        )
      SELECT stock_move.id AS res_id,
             'stock.move' AS res_model,
             'l10n_ke_oscu_attachment_file' AS res_field,
             {cols_prefix}
        FROM ir_attachment att
        JOIN stock_move
          ON att.id = stock_move.l10n_ke_oscu_attachment_id
       WHERE att.res_model = 'stock.picking'
        """,
        columns=cols,
        cols_prefix=cols.using(alias="att"),
    )
    cr.execute(query)

    util.remove_field(cr, "stock.move", "l10n_ke_oscu_attachment_id")
