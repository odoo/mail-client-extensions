# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'maintenance_equipment_category', 'company_id', 'int4')
    util.create_column(cr, 'maintenance_equipment', 'company_id', 'int4')
    util.create_column(cr, 'maintenance_request', 'company_id', 'int4')
    util.create_column(cr, 'maintenance_team', 'company_id', 'int4')
    util.create_column(cr, 'maintenance_team', 'active', 'boolean')
    cr.execute("UPDATE maintenance_team SET active=true")

    util.rename_field(cr, 'maintenance.equipment', 'warranty', 'warranty_date')
