# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.recompute_fields(cr, "hr.leave", ["number_of_hours"])
