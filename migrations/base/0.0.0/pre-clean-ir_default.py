from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.table_exists(cr, "ir_default"):
        cr.execute(
            """
            DELETE FROM ir_default d
             USING ir_model_fields imf
             WHERE d.field_id = imf.id
               AND imf.required IS TRUE
               AND CASE imf.ttype
                       WHEN 'selection' THEN d.json_value = '""'
                       WHEN 'many2one' THEN d.json_value IN ('""', 'false', '0', 'null')
                       ELSE false
                   END
            """
        )
