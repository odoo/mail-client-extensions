# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_m2m(cr, 'maintenance_team_users_rel', 'maintenance_team', 'res_users')
    cr.execute("""
        INSERT INTO maintenance_team_users_rel(maintenance_team_id, res_users_id)
             SELECT t.id, u.id
               FROM maintenance_team t
               JOIN res_users u ON (t.partner_id = u.partner_id)
    """)
    util.remove_field(cr, 'maintenance.team', 'partner_id')
