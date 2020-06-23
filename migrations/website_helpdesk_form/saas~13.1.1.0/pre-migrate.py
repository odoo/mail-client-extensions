# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "helpdesk_team", "website_form_view_id", "int4")

    util.remove_view(cr, "website_helpdesk_form.ticket_submit")
