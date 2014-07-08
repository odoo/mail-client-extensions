# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'project_issue', 'channel', 'character varying')
    cr.execute("""
		UPDATE project_issue 
		SET channel = cc.name
		FROM crm_case_channel cc
		where project_issue.channel_id = cc.id
	""")
