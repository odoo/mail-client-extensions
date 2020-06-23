# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "digest_tip", "name", "varchar")
    cr.execute("UPDATE digest_tip SET name = CONCAT('Tip #', id)")
