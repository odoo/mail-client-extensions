# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    eb = util.expand_braces

    views = [
        eb('payment_{0}.{0}_{{acquirer_button,form}}'.format(mod))
        for mod in 'adyen authorize buckaroo ogone paypal payumoney sips stripe transfer'.split()
    ]
    views.append(eb('payment.default_acquirer_button{-todel,}'))

    for old, new in views:
        util.replace_record_references(
            cr,
            ('ir.ui.view', util.ref(cr, old)),
            ('ir.ui.view', util.ref(cr, new)),
            replace_xmlid=False)

        util.remove_view(cr, old)
