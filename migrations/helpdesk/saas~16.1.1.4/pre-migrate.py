# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.update_field_references(cr, "email", "partner_email", only_models=("helpdesk.ticket",))
    util.remove_field(cr, "helpdesk.ticket", "email")
