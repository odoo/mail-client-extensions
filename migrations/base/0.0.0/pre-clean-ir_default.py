from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.table_exists(cr, "ir_default"):
        cr.execute(
            """
            DELETE FROM ir_default d
             USING ir_model_fields f
             WHERE d.field_id = f.id
               AND f.required IS TRUE
               AND f.ttype = 'selection'
               AND d.json_value = '""'
            """
        )
