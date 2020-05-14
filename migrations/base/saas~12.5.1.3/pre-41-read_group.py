# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations._lib2to3_fixers import RefactoringTool

refactoring_tool = RefactoringTool(["odoo.addons.base.maintenance.migrations._lib2to3_fixers.read_group"])


def migrate(cr, version):
    refactor_read_group(cr, "ir_act_server", "code")
    refactor_read_group(cr, "ir_model_fields", "compute")


def refactor_read_group(cr, table, column):
    cr.execute(
        rf"""
            SELECT id, {column}
              FROM {table}
             WHERE {column} like '%read\_group%'
         """
    )
    for id, code in cr.fetchall():
        # Force adding a carriage return before sending to `RefactoringTool`, and then remove it
        # because `RefactoringTool` cries when refactoring code without an ending carriage return.
        new_code = str(refactoring_tool.refactor_string(code + "\n", "script"))[:-1]
        if new_code != code:
            cr.execute(
                f"""
                    UPDATE {table}
                       SET {column} = %s
                     WHERE id = %s
                """,
                (new_code, id),
            )
