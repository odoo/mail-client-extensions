# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):

    # website.layout changed in an incompatible manner at fe3775b and
    # will always be forced-reset, so we need to reset this one too,
    # as it inherits from a different template now!
    # Theoretically it only adds a small "Resellers" link in the footer,
    # so customizations are unlikely.
    util.force_noupdate(cr, 'website_crm_partner_assign.footer_custom', False)

