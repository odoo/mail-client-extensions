# -*- coding: utf-8 -*-

from odoo import modules

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.table_exists(cr, "ir_model_fields_selection"):
        cr.execute(
            """
            INSERT INTO ir_model_data(module,name,model,res_id,noupdate,create_date)
            SELECT d2.module,
                   d.name,
                   d.model,
                   d.res_id,
                   false,
                   now() at time zone 'UTC'
              FROM ir_model_data d
              JOIN ir_model_fields_selection s
                ON d.res_id = s.id
               AND d.model = 'ir.model.fields.selection'
              JOIN ir_model_fields f
                ON s.field_id = f.id
              JOIN ir_model_data d2
                ON d2.res_id = f.model_id
               AND d2.model = 'ir.model'
             WHERE d.module = ANY(%(standard_modules)s)
               AND d2.module != ALL(%(standard_modules)s)
                ON CONFLICT DO NOTHING
      """,
            {"standard_modules": list(modules.get_modules())},
        )
