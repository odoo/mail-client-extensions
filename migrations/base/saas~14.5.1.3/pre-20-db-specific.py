# -*- coding: utf-8 -*-
from odoo.upgrade import util


def _db_openerp(cr, version):
    util.module_deps_diff(
        cr,
        "openerp_website",
        plus={"appointment", "mail_group"},
        minus={"website_calendar", "website_animate", "website_mail_channel"},
    )
    util.remove_module(cr, "payment_authorize_ach")


def migrate(cr, version):
    util.dispatch_by_dbuuid(cr, version, {"8851207e-1ff9-11e0-a147-001cc0f2115e": _db_openerp})
