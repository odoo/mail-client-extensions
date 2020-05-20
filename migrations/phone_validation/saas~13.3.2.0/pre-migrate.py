# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "mail.thread.phone", "phone_blacklisted", "phone_sanitized_blacklisted")
