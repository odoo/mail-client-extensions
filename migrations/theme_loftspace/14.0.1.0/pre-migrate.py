# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # remove view loading deprecated snippet files
    util.remove_record(cr, "theme_loftspace._assets_primary_variables")
