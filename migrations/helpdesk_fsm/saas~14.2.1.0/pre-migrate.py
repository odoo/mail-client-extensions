# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "helpdesk_team", "fsm_project_id", "int4")
    cr.execute("SELECT id FROM project_project WHERE is_fsm = true AND active = true ORDER BY sequence,id LIMIT 1")
    [project_id] = cr.fetchone() or [False]
    if project_id:
        cr.execute("""UPDATE helpdesk_team SET fsm_project_id = %s WHERE use_fsm = true""", [project_id])
