# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, 'mass_mailing_sms.mailing_contact_view_tree_sms')
    util.force_noupdate(cr, 'mass_mailing_sms.mailing_contact_view_search', False)
    util.force_noupdate(cr, 'mass_mailing_sms.mailing_contact_view_form', False)
    util.force_noupdate(cr, 'mass_mailing_sms.mailing_contact_view_kanban', False)
    util.force_noupdate(cr, 'mass_mailing_sms.mailing_contact_action_sms', False)

    util.rename_field(cr, "mailing.contact", "phone_blacklisted", "phone_sanitized_blacklisted")
