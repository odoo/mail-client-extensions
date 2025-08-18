from odoo.upgrade import util


def migrate(cr, version):
    # We remove this view explicitly to force the creation of the new one
    util.remove_view(cr, "account_followup.template_followup_report")
    util.remove_view(cr, "account_followup.followup_search_template")
    util.remove_view(cr, "account_followup.cell_template_followup_report")
    util.remove_view(cr, "account_followup.followup_filter_info_template")

    util.create_column(cr, "res_partner", "followup_reminder_type", "varchar", default="automatic")
