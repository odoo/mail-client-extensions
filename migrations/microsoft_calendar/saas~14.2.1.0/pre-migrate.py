# -*- coding:utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    """
    microsoft_calendar add stop synchronization (PR: 60825 community).
    """

    util.create_column(cr, "res_users", "microsoft_synchronization_stopped", "boolean")
