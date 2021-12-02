# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    if util.has_enterprise():
        # merges
        util.merge_module(cr, "website_helpdesk_form", "website_helpdesk")

    util.modules_auto_discovery(cr)
