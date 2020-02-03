# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    eb = util.expand_braces
    util.force_noupdate(cr, "mass_mailing.mass_mailing_mail_layout", True)

    views = util.splitlines(
        """
        mass_mailing_mail_style

        view_mail_mass_mailing_stage_search
        view_mail_mass_mailing_stage_tree
        mail_mass_mailing_tag_view_form
    """
    )
    for v in views:
        util.remove_view(cr, "mass_mailing." + v)

    util.remove_record(cr, "mass_mailing.action_view_mass_mailing_stages")
    util.remove_record(cr, "mass_mailing.mass_mailing_tag_action")

    util.rename_xmlid(
        cr, "mass_mailing.view_mail_statistics_report_pivot", "mass_mailing.mailing_trace_report_view_pivot"
    )
    util.rename_xmlid(
        cr, "mass_mailing.view_mail_statistics_report_graph", "mass_mailing.mailing_trace_report_view_graph"
    )
    util.rename_xmlid(
        cr, "mass_mailing.view_mail_statistics_report_search", "mass_mailing.mailing_trace_report_view_search"
    )
    util.rename_xmlid(cr, "mass_mailing.action_mail_statistics_report", "mass_mailing.mailing_trace_report_action_mail")

    util.rename_xmlid(cr, *eb("mass_mailing.access_{mass_mailing_tag,utm_tag_mass_mailing_campaign}"))
    util.rename_xmlid(cr, *eb("mass_mailing.access_{mass_mailing_contact,mailing_contact_mm_user}"))
    util.rename_xmlid(cr, *eb("mass_mailing.access_{mass_mailing_list,mailing_list_mm_user}"))
    util.rename_xmlid(cr, *eb("mass_mailing.access_{mass_mailing,utm}_stage"))
    util.rename_xmlid(cr, *eb("mass_mailing.access_{mass_mailing,mailing_mailing_mm_user}"))
    util.rename_xmlid(cr, *eb("mass_mailing.access_{mass,mailing}_mailing_system"))
    util.rename_xmlid(cr, *eb("mass_mailing.access_{mail_mail_statistics,mailing_trace}_user"))
    util.rename_xmlid(cr, *eb("mass_mailing.access_{mail_mail_statistics_mass_mailing,mailing_trace_mm}_user"))
    util.rename_xmlid(cr, *eb("mass_mailing.access_{mail_mail_statistics_report,mailing_trace_report_mm_user}"))

    util.rename_xmlid(cr, "mass_mailing.view_mail_mail_statistics_search", "mass_mailing.mailing_trace_view_search")
    util.rename_xmlid(cr, "mass_mailing.view_mail_mail_statistics_tree", "mass_mailing.mailing_trace_view_tree")
    util.rename_xmlid(cr, "mass_mailing.view_mail_mail_statistics_form", "mass_mailing.mailing_trace_view_form")
    util.rename_xmlid(cr, "mass_mailing.action_view_mail_mail_statistics", "mass_mailing.mailing_trace_action")

    util.remove_record(cr, "mass_mailing.action_view_mail_mail_statistics_mailing_list")

    util.rename_xmlid(
        cr, *eb("mass_mailing.{mail_mass_mailing_list_contact_rel,mailing_contact_subscription}_view_form")
    )
    util.rename_xmlid(
        cr, *eb("mass_mailing.{mail_mass_mailing_list_contact_rel_list_contact,mailing_contact_subscription}_view_tree")
    )
    util.rename_xmlid(
        cr, *eb("mass_mailing.{mail_mass_mailing_list_contact_rel,mailing_contact_subscription}_view_form")
    )
    util.rename_xmlid(
        cr,
        "mass_mailing.mail_mass_mailing_list_contact_view_search",
        "mass_mailing.mailing_contact_subscription_view_search",
    )
    util.remove_record(cr, "mass_mailing.action_view_mass_mailing_contacts_from_list")

    for mode in {"search", "tree", "form", "form_simplified", "kanban"}:
        util.rename_xmlid(
            cr, "mass_mailing.view_mail_mass_mailing_list_" + mode, "mass_mailing.mailing_list_view_" + mode
        )

    util.rename_xmlid(cr, "mass_mailing.action_view_mass_mailings", "mass_mailing.mailing_mailing_action_mail")
    util.remove_record(cr, "mass_mailing.action_create_ab_mass_mailings_from_campaign")

    util.rename_xmlid(cr, *eb("mass_mailing.{mass_,}mailing_list_merge_view_form"))
    util.rename_xmlid(cr, *eb("mass_mailing.{mass_,}mailing_list_merge_action"))
    util.rename_xmlid(cr, *eb("mass_mailing.{mass,mailing}_mailing_schedule_date_view_form"))
    util.rename_xmlid(cr, *eb("mass_mailing.{mass,mailing}_mailing_schedule_date_action"))
