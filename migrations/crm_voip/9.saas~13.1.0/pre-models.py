# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_field(cr, 'crm.phonecall', 'priority')
    util.remove_field(cr, 'crm.phonecall', 'categ_id')
    util.remove_field(cr, 'crm.phonecall.report', 'categ_id')

    util.remove_field(cr, 'crm.phonecall.log.wizard', 'opportunity_title_action')
    util.remove_field(cr, 'crm.phonecall.log.wizard', 'opportunity_date_action')

    util.delete_model(cr, 'crm.phonecall.category')
    util.delete_model(cr, 'crm.custom.phonecall.wizard')
    util.delete_model(cr, 'crm.phonecall2phonecall')
