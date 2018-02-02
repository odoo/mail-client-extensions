# -*- coding: utf-8 -*-
import logging
import os
from odoo.addons.base.maintenance.migrations import util

NS = 'odoo.addons.base.maintenance.migrations.base.saas~18.'
_logger = logging.getLogger(NS + __name__)

def _db_openerp(cr, version):
    util.remove_model(cr, 'board.board.line')   # should have been remove during 6.1 -> 7.0 migration

    cr.execute("""
        DELETE FROM openerp_enterprise_database_app WHERE module_id IN (
            SELECT id
              FROM ir_module_module
             WHERE name = 'project_issue'
        )
    """)
    cr.execute("""
        UPDATE openerp_enterprise_database_app
           SET name = 'voip',
               shortdesc = 'VOIP',
               module_id = (SELECT id FROM ir_module_module WHERE name='voip')
         WHERE module_id = (SELECT id FROM ir_module_module WHERE name='crm_voip')
    """)
    cr.execute("""
        UPDATE openerp_enterprise_database_app
           SET name = 'sale_subscription',
               shortdesc = 'Subscription Management',
               module_id = (SELECT id FROM ir_module_module WHERE name='sale_subscription')
         WHERE module_id = (SELECT id FROM ir_module_module WHERE name='website_subscription')
    """)

    util.remove_view(cr, view_id=8977)      # duplicated view
    util.remove_view(cr, view_id=1876)      # old issue view
    util.remove_view(cr, view_id=10011)
    util.remove_view(cr, view_id=10308)     # sale.quote.template.active.dbo

    cr.execute("UPDATE ir_ui_view SET arch_db=replace(arch_db, '2653', '3229') WHERE id=8118")

    util.force_noupdate(cr, 'openerp_website.odoo_blog_main_column', False)

    # do no split some projects
    os.environ['ODOO_MIG_S18_NOSPLIT_PROJECTS'] = '49,809,250,133,637,129'

def migrate(cr, version):
    util.dispatch_by_dbuuid(cr, version, {
        '8851207e-1ff9-11e0-a147-001cc0f2115e': _db_openerp,
    })
