# -*- coding:utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    """
    google_calendar add stop synchronization (PR: 60825 community).
    """

    util.create_column(cr, "res_users", "google_synchronization_stopped", "boolean")
