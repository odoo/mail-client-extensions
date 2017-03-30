# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_field(cr, 'mass.mailing.config.settings', 'group_mass_mailing_campaign')
