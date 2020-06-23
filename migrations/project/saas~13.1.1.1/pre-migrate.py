# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.move_field_to_module(cr, "project.task", "partner_email", "project_enterprise", "project")
    util.move_field_to_module(cr, "project.task", "partner_phone", "project_enterprise", "project")
