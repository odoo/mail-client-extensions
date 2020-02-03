# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.rename_xmlid(cr, "mass_mailing_crm.mail_mass_mailing_view_form", "mass_mailing_crm.mailing_mailing_view_form")
