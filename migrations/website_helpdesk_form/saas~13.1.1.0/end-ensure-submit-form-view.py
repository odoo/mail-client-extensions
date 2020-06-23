# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    teams = util.env(cr)["helpdesk.team"].search([("use_website_helpdesk_form", "=", True)])
    teams._ensure_submit_form_view()
