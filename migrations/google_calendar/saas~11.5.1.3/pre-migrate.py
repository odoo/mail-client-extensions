# -*- coding: utf-8 -*-
from odoo import SUPERUSER_ID


def migrate(cr, version):
    cr.execute("UPDATE res_users SET google_calendar_token = NULL WHERE id = %s", [SUPERUSER_ID])
