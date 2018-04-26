# -*- coding: utf-8 -*-
import psycopg2
from odoo.tools.misc import ignore
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    xid = '{0}.view_company_form_inherit_{0}'.format
    if util.rename_xmlid(cr, xid('website'), xid('social_media')):
        util.remove_view(cr, xid('mass_mailing'))
    else:
        util.rename_xmlid(cr, xid('mass_mailing'), xid('social_media'))
    # move social fields
    for network in 'twitter facebook github linkedin youtube googleplus'.split():
        field = 'social_' + network
        util.move_field_to_module(cr, 'res.company', field, 'website', 'social_media')
        with ignore(psycopg2.Error), util.savepoint(cr):
            util.move_field_to_module(cr, 'res.company', field, 'mass_mailing', 'social_media')
