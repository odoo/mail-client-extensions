# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util
def migrate(cr, version):
    # m2o function fields now have foreign keys...
    util.ensure_m2o_func_field_data(cr, 'mail_mail_statistics', 'mass_mailing_campaign_id', 'mail_mass_mailing_campaign')
