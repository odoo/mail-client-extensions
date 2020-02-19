# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "helpdesk.ticket", "is_overdue")
    util.rename_field(
        cr, "helpdesk.ticket", "is_so_button_visible", "display_create_so_button_primary", update_references=True
    )
