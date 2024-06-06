from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(cr, "data_cleaning.merge_action_utm_campaign", "data_merge_utm.merge_action_utm_campaign")
    util.rename_xmlid(cr, "data_cleaning.merge_action_utm_medium", "data_merge_utm.merge_action_utm_medium")
    util.rename_xmlid(cr, "data_cleaning.merge_action_utm_source", "data_merge_utm.merge_action_utm_source")
