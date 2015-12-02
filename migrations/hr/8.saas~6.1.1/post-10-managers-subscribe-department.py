# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    env = util.env(cr)
    Dep = env['hr.department'].with_context(mail_create_nosubscribe=True)
    cr.execute("""
        SELECT d.id, r.user_id
          FROM hr_department d
          JOIN hr_employee e ON (e.id = d.manager_id)
          JOIN resource_resource r ON (r.id = e.resource_id)
    """)
    for dep_id, user_id in cr.fetchall():
        Dep.browse(dep_id).message_subscribe_users(user_ids=[user_id])
