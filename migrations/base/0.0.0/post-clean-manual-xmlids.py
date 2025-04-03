# -*- coding: utf-8 -*-
from odoo import modules

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    standard_modules = modules.get_modules()
    excluded_modules = {"studio_customization", "__cloc_exclude__"}
    included_modules = {"__export__"}
    modules_that_should_not_have_manual_fields_xmlid = set(standard_modules) - excluded_modules | included_modules

    query = util.format_query(
        cr,
        """
        DELETE
          FROM ir_model_data d
         USING ir_model_fields f,
               ir_model m
         WHERE d.model = 'ir.model.fields'
           AND f.id = d.res_id
           AND m.id = f.model_id
           AND f.state = 'manual'
           AND m.state = 'base'
           AND d.module IN %s
            {}
        """,
        util.SQLStr("AND d.studio IS NOT TRUE" if util.column_exists(cr, "ir_model_data", "studio") else ""),
    )
    cr.execute(query, [tuple(modules_that_should_not_have_manual_fields_xmlid)])
