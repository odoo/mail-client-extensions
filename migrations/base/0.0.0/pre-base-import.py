from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.version_between("saas~17.4", "19.0") and util.column_exists(cr, "ir_module_module", "imported"):
        # remove fake dependencies created by a bug in base_import_module
        cr.execute(
            """
            WITH invalid_deps AS (
                SELECT d.id
                  FROM ir_module_module_dependency d
                  JOIN ir_module_module i
                    ON d.module_id = i.id
             LEFT JOIN ir_module_module m
                    ON d.name = m.name
                 WHERE m.id IS NULL
                   AND i.imported
            )
            DELETE FROM ir_module_module_dependency dep
                  USING invalid_deps
                  WHERE dep.id = invalid_deps.id
            """
        )
