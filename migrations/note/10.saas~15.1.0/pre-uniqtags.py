# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.uniq_tags(cr, 'note.tag', 'lower(name)')
