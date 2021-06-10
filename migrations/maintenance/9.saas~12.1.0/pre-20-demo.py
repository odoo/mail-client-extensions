# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("maintenance.{hr_,}equipment_phone"))
    util.rename_xmlid(cr, *eb("maintenance.{hr_,}equipment_printer1"))
    for suffix in {"", 1, 4, 6}:
        util.rename_xmlid(cr, *eb("maintenance.{hr_,}equipment_monitor%s" % suffix))
    for suffix in {3, 5, 9, 11}:
        util.rename_xmlid(cr, *eb("maintenance.{hr_,}equipment_computer%s" % suffix))
