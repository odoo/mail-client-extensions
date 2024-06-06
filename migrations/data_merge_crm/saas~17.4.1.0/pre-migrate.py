from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(cr, "data_cleaning.merge_action_crm_lost_reason", "data_merge_crm.merge_action_crm_lost_reason")
    util.rename_xmlid(cr, "data_cleaning.merge_action_crm_tag", "data_merge_crm.merge_action_crm_tag")
