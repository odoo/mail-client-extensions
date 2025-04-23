from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.merge_model(cr, *eb("im_livechat.report.{operator,channel}"))
    cr.execute("DROP VIEW IF EXISTS im_livechat_report_operator")
    util.remove_view(cr, "im_livechat.im_livechat_report_operator_view_graph")
    util.remove_view(cr, "im_livechat.im_livechat_report_operator_view_pivot")
    util.remove_view(cr, "im_livechat.im_livechat_report_operator_view_search")
    cr.execute("DROP VIEW IF EXISTS im_livechat_report_channel")
    util.remove_field(cr, "im_livechat.report.channel", "days_of_activity")
    util.remove_field(cr, "im_livechat.report.channel", "is_anonymous")
    util.remove_field(cr, "im_livechat.report.channel", "is_happy")
    util.remove_field(cr, "im_livechat.report.channel", "is_unrated")
    util.remove_field(cr, "im_livechat.report.channel", "is_without_answer")
    util.remove_field(cr, "im_livechat.report.channel", "nbr_channel")
    util.remove_field(cr, "im_livechat.report.channel", "nbr_speaker")
    util.remove_field(cr, "im_livechat.report.channel", "technical_name")
