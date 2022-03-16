# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.ENVIRON["__no_model_data_delete"]["stock.location"] = "always"
    util.ENVIRON["__no_model_data_delete"]["stock.rule"] = "always"
    util.ENVIRON["__no_model_data_delete"]["stock.picking.type"] = "unused"
    util.ENVIRON["__no_model_data_delete"]["stock.warehouse"] = "unused"
