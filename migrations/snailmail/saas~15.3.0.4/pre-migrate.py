# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_model(cr, "snailmail.letter.cancel", drop_table=True)
