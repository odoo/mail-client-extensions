# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, 'hr.employee', 'medic_exam')
    util.remove_field(cr, 'res.users', 'medic_exam')
