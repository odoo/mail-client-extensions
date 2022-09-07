# -*- coding: utf-8 -*-

from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # Removed deprecated mail template
    util.remove_record(cr, "website_quote.email_template_edi_sale")
