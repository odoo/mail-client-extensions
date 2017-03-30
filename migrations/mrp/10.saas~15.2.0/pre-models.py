# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    fields = util.splitlines("""
        group_product_variant
        module_mrp_byproduct
        module_mrp_mps
        module_mrp_plm
        module_mrp_maintenance
        module_quality_mrp
        group_mrp_groupings
    """)
    for f in fields:
        util.remove_field(cr, 'mrp.config.settings', f)

    util.create_column(cr, 'mrp_workcenter', 'name', 'varchar')
    util.create_column(cr, 'mrp_workcenter', 'time_efficiency', 'float8')
    util.create_column(cr, 'mrp_workcenter', 'active', 'boolean')
    util.create_column(cr, 'mrp_workcenter', 'code', 'varchar')
    util.create_column(cr, 'mrp_workcenter', 'company_id', 'int4')
    cr.execute("""
        UPDATE mrp_workcenter w
           SET name = r.name,
               time_efficiency = r.time_efficiency,
               active = r.active,
               code = r.code,
               company_id = r.company_id
          FROM resource_resource r
         WHERE r.id = w.resource_id
    """)
