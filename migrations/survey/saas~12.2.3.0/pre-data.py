# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    eb = util.expand_braces

    util.rename_xmlid(cr, "survey.email_template_survey", "survey.mail_template_user_input_invite")
    util.delete_unused(cr, "survey.stage_permanent")

    for x in {"", "_question", "_label", "_user_input", "_user_input_line", "_stage"}:
        util.rename_xmlid(cr, *eb("survey.access_survey%s_{public,all}" % x), False)
        util.rename_xmlid(cr, *eb("survey.access_survey%s_{,survey_}user" % x), False)
        util.rename_xmlid(cr, *eb("survey.access_survey%s_{,survey_}manager" % x), False)

    util.remove_record(cr, "survey.survey_input_public_access")
    util.rename_xmlid(cr, "survey.survey_manager_access", "survey.survey_survey_rule_survey_manager")

    for infix in {"users", "input_public", "input_users", "input_manager"}:
        util.remove_record(cr, "survey.survey_{}_access".format(infix))

    util.remove_record(cr, "survey.act_survey_pages")
    util.remove_record(cr, "survey.act_survey_question")

    util.rename_xmlid(cr, "survey.nopages", "survey.survey_void")
    util.remove_view(cr, "survey.notopen")
    util.remove_view(cr, "survey.no_result")
    util.force_noupdate(cr, "survey.page", False)

    util.rename_xmlid(cr, "survey.action_selected_survey_user_input", "survey.action_survey_user_input_notest", False)
