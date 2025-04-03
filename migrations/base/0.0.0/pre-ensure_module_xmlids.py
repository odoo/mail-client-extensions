# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    module_name = "REPLACE(m.name, ' ', '_')" if util.version_gte("15.0") else "m.name"
    query = util.format_query(
        cr,
        """
        INSERT INTO ir_model_data(module, name, res_id, model, noupdate)
        SELECT 'base', 'module_' || {}, m.id, 'ir.module.module', true
          FROM ir_module_module m
   ON CONFLICT DO NOTHING
        """,
        util.SQLStr(module_name),
    )
    cr.execute(query)
