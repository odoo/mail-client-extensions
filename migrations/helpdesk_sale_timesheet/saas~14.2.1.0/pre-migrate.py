# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "helpdesk_ticket", "sale_line_id", "int4")
    util.remove_field(cr, "helpdesk.ticket", "display_create_so_button_primary")
    util.remove_field(cr, "helpdesk.ticket", "display_create_so_button_secondary")
    util.remove_field(cr, "helpdesk.ticket", "sale_line_id_source")
