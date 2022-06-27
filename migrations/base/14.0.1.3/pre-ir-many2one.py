from odoo.fields import IR_MODELS


def migrate(cr, version):
    cr.execute(
        """
         UPDATE ir_model_fields
            SET on_delete = (CASE WHEN required THEN 'cascade' ELSE 'set null' END)
          WHERE relation = ANY(%s)
            AND on_delete = 'restrict'
            AND ttype = 'many2one'
        """,
        [list(IR_MODELS)],
    )
