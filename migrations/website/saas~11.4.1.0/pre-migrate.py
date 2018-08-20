# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_view(cr, "website.footer_default")  # haters gonna hate...
    util.force_noupdate(cr, "website.layout_footer_copyright", False)
