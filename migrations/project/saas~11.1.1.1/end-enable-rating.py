# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    cr.execute("""
        SELECT count(1)
          FROM rating_rating
         WHERE res_model='project.task'
    """)
    if cr.fetchone()[0] > 0:
        util.env(cr)['res.config.settings'].create({'group_project_rating': True}).execute()
