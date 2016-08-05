# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def _db_openerp(cr, version):
    util.force_noupdate(cr, 'openerp_website.odoo_blog_sidebar_blogs', False)
    util.remove_view(cr, view_id=8816)      # custom inherited view now builtin
    util.remove_view(cr, view_id=8978)      # please define xmlids when creating views manually...

def _db_natural_fresh(cr, version):
    cr.execute("DELETE FROM ir_model_fields WHERE id=5754")
    cr.execute("select id from ir_ui_view where arch_db like '%x\_claim\_ids%'")
    for vid, in cr.fetchall():
        util.remove_view(cr, view_id=vid)

def _boldom(cr, version):
    cr.execute("DELETE FROM ir_server_object_lines WHERE id=403")
    cr.execute("UPDATE ir_ui_view SET arch_db=%s WHERE id=837",
               ["""<xpath expr="//field[@name='fax']/.."><group/></xpath>"""])

def migrate(cr, version):
    util.dispatch_by_dbuuid(cr, version, {
        '05a64ced-5b98-488d-a833-a994f9b1dd80': _db_openerp,    # test
        '8851207e-1ff9-11e0-a147-001cc0f2115e': _db_openerp,    # prod
        '676796d7-881a-42c1-b5c8-ecae4452ec23': _db_natural_fresh,
        '39b15f26-b737-4420-94bb-156191526fbf': _boldom,
    })
