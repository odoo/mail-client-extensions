# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def _db_openerp(cr, version):
    util.force_noupdate(cr, 'openerp_website.odoo_blog_sidebar_blogs', False)
    util.remove_view(cr, view_id=8816)      # custom inherited view now builtin
    util.remove_view(cr, view_id=8978)      # please define xmlids when creating views manually...


def migrate(cr, version):
    util.dispatch_by_dbuuid(cr, version, {
        '05a64ced-5b98-488d-a833-a994f9b1dd80': _db_openerp,    # test
        '8851207e-1ff9-11e0-a147-001cc0f2115e': _db_openerp,    # prod
    })
