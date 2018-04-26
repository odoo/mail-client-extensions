# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_field(cr, 'signature.request', 'archived', 'active')
    util.rename_field(cr, 'signature.request.template', 'archived', 'active')

    cr.execute("UPDATE signature_request SET active=not active")
    cr.execute("UPDATE signature_request_template SET active=not active")
