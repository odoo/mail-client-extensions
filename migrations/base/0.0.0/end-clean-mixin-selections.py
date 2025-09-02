from odoo import modules

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.table_exists(cr, "ir_model_fields_selection"):
        standard_modules = set(modules.get_modules()) - {"studio_customization", "__cloc_exclude__", "__export__"}

        cr.execute(
            """
            WITH unloaded_models AS (
                SELECT m.model
                  FROM ir_model m
                  JOIN ir_model_data d
                    ON d.res_id = m.id
                   AND d.model = 'ir.model'
                  JOIN ir_module_module mm
                    ON d.module = mm.name
                 WHERE mm.name IN %s
                 GROUP BY m.model
                HAVING BOOL_AND(mm.state = 'uninstalled')
            )
            SELECT s.id
              FROM ir_model_fields_selection s
              JOIN ir_model_data d
                ON d.model = 'ir.model.fields.selection'
               AND s.id = d.res_id
              JOIN ir_model_fields f
                ON f.id = s.field_id
              JOIN unloaded_models
                ON f.model = unloaded_models.model
              JOIN ir_module_module m
                ON m.name = d.module
             WHERE m.state = 'installed'
               AND m.name IN %s
            """,
            [tuple(standard_modules), tuple(standard_modules)],
        )
        util.remove_records(cr, "ir.model.fields.selection", [id[0] for id in cr.fetchall()])
