# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "event.type", "use_ticket")
    util.remove_field(cr, "event.type", "use_mail_schedule")
    util.remove_field(cr, "event.type", "use_timezone")
    util.create_column(cr, "event_type", "note", "text")
