# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute("DELETE FROM ir_model_data WHERE module='resource' and name='_init_data_resource_calendar'")
