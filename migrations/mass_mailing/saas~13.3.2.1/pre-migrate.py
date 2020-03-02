# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, 'utm.campaign', 'mailing_clicks_ratio')
    util.remove_field(cr, 'utm.campaign', 'mailing_items')
    util.remove_field(cr, 'utm.campaign', 'mailing_clicked')
    util.remove_field(cr, 'utm.campaign', 'total')
    util.remove_field(cr, 'utm.campaign', 'scheduled')
    util.remove_field(cr, 'utm.campaign', 'failed')
    util.remove_field(cr, 'utm.campaign', 'ignored')
    util.remove_field(cr, 'utm.campaign', 'sent')
    util.remove_field(cr, 'utm.campaign', 'delivered')
    util.remove_field(cr, 'utm.campaign', 'opened')
    util.remove_field(cr, 'utm.campaign', 'replied')
    util.remove_field(cr, 'utm.campaign', 'bounced')

    util.rename_xmlid(cr, 'mass_mailing.view_mail_mass_mailing_contact_search', 'mass_mailing.mailing_contact_view_search')
    util.rename_xmlid(cr, 'mass_mailing.view_mail_mass_mailing_contact_form', 'mass_mailing.mailing_contact_view_form')
    util.rename_xmlid(cr, 'mass_mailing.view_mail_mass_mailing_contact_tree', 'mass_mailing.mailing_contact_view_tree')
    util.rename_xmlid(cr, 'mass_mailing.view_mail_mass_mailing_contact_kanban', 'mass_mailing.mailing_contact_view_kanban')
    util.rename_xmlid(cr, 'mass_mailing.view_mail_mass_mailing_contact_pivot', 'mass_mailing.mailing_contact_view_pivot')
    util.rename_xmlid(cr, 'mass_mailing.view_mail_mass_mailing_contact_graph', 'mass_mailing.mailing_contact_view_graph')
