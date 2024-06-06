from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(
        cr, "data_cleaning.merge_action_helpdesk_ticket", "data_merge_helpdesk.merge_action_helpdesk_ticket"
    )
    util.rename_xmlid(cr, "data_cleaning.merge_action_helpdesk_tag", "data_merge_helpdesk.merge_action_helpdesk_tag")
