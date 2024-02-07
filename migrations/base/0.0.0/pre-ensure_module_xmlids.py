# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute(
        """
        INSERT INTO ir_model_data(module, name, res_id, model, noupdate)
        SELECT 'base', 'module_' || m.name, m.id, 'ir.module.module', true
          FROM ir_module_module m
   ON CONFLICT DO NOTHING
        """
    )
