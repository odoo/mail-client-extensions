# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.ENVIRON["__no_model_data_delete"]["crm.stage"] = "unused"
