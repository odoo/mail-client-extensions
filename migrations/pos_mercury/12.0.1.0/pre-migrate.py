# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.rename_xmlid(cr, *util.expand_braces("pos_mercury.{pos,res}_config_view_form_inherit_pos_mercury"))
