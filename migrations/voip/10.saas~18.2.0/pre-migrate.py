# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    eb = util.expand_braces

    for icp in 'pbx_ip wsServer mode'.split():
        cr.execute("UPDATE ir_config_parameter SET key=%s WHERE key=%s",
                   ['voip.' + icp, 'crm.voip.' + icp])

    util.create_column(cr, 'res_partner', 'sanitized_phone', 'varchar')
    util.create_column(cr, 'res_partner', 'sanitized_mobile', 'varchar')

    util.remove_field(cr, 'res.user', 'sip_ring_number')
    util.remove_field(cr, 'crm.lead', 'in_call_center_queue')

    util.remove_model(cr, 'crm.phonecall.report')
    util.remove_model(cr, 'crm.schedule_phonecall')
    util.remove_model(cr, 'crm.phonecall.log.wizard')   # easier that renaming+cleaning

    if util.table_exists(cr, 'crm_phonecall'):
        util.rename_model(cr, 'crm.phonecall', 'voip.phonecall')
        util.remove_field(cr, 'voip.phonecall', 'company_id')
        util.remove_field(cr, 'voip.phonecall', 'team_id')
        util.remove_field(cr, 'voip.phonecall', 'opportunity_id')
        util.rename_field(cr, 'voip.phonecall', 'date', 'call_date')
        util.rename_field(cr, 'voip.phonecall', 'description', 'note')
        util.rename_field(cr, 'voip.phonecall', 'partner_phone', 'phone')
        util.rename_field(cr, 'voip.phonecall', 'partner_mobile', 'mobile')
        cr.execute("UPDATE voip_phonecall SET note = {}".format(util.pg_text2html('note')))

        util.rename_model(cr, *eb('{crm,voip}.phonecall.transfer.wizard'))

    util.remove_record(cr, 'voip.action_create_call_in_queue')
    util.remove_view(cr, 'voip.lead_button_call_kanban_view')
    util.remove_view(cr, 'voip.lead_button_voip_view')

    util.rename_xmlid(cr, *eb('voip.{crm,voip}_phonecall_tree_view'))
    util.rename_xmlid(cr, *eb('voip.view_{crm,voip}_case_phonecalls_filter'))
    util.rename_xmlid(cr, *eb('voip.{crm,voip}_phonecalls_view'))   # which is actually an action
    util.rename_xmlid(cr, *eb('voip.menu_{crm,voip}_phonecalls_view'))
