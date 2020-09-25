# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.force_noupdate(cr, "utm.campaign_stage_1", True)
    util.force_noupdate(cr, "utm.campaign_stage_2", True)
    util.force_noupdate(cr, "utm.campaign_stage_3", True)
