# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def _openerp(cr, version):
    # Set Olivia as responsible for belgian `hr` leave types
    cr.execute("""
        UPDATE hr_leave_type
           SET responsible_id = 933484
         WHERE validation_type = 'hr'
           AND company_id = 1
    """)


def migrate(cr, version):
    util.dispatch_by_dbuuid(cr, version, {
        "8851207e-1ff9-11e0-a147-001cc0f2115e": _openerp,
    })
