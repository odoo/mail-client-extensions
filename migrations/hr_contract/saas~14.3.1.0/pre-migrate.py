# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_menus(cr, [util.ref(cr, "hr_contract.hr_menu_contract")])
