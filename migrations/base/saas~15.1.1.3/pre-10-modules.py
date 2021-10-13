# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.modules_auto_discovery(cr)

    util.remove_module(cr, "note_pad")
    util.remove_module(cr, "pad_project")
    util.remove_module(cr, "pad")
