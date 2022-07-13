# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "mail.test.track.selection", "type", "selection_type")
