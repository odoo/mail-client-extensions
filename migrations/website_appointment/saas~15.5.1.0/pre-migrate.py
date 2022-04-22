# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_appointment.user_navbar_inherit_website_enterprise_inherit_website_appointment")
