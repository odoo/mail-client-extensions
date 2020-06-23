# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "mail_channel", "active", "boolean")
    cr.execute("UPDATE mail_channel SET active=true")

    util.remove_record(cr, "mail.mail_followers_read_write_own")
