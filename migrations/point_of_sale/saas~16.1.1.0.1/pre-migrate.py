# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "pos.config", "number_of_opened_session", "number_of_rescue_session")
