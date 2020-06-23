# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    fm = util.import_script("website/saas~13.2.1.0/fixmixin.py")
    fm.replace_resize_class(cr, "event.event")
