# -*- coding: utf-8 -*-
import logging

from odoo.addons.base.maintenance.migrations import util

rules = util.import_script("base/0.0.0/init-rules.py")


def migrate(cr, version):
    rules.optimize_rules(cr, logging.getLogger(__name__))
