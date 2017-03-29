# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # sparse fields
    cr.execute("SELECT count(1) FROM ir_model_fields WHERE ttype='serialized'")
    has_sparse_fields = bool(cr.fetchone()[0])

    util.new_module(cr, 'base_sparse_field', ('base',), auto_install=has_sparse_fields)

    util.remove_module_deps(cr, 'hr_holidays', ('product',))
    util.remove_module_deps(cr, 'hr_recruitment', ('decimal_precision', 'web_kanban_gauge'))

    util.new_module_dep(cr, 'l10n_ch', 'base_iban')
    util.new_module_dep(cr, 'website_portal', 'portal')     # seriously, wasn't already the case?

    util.new_module(cr, 'website_sale_comparison', ('website_sale',))
    util.new_module(cr, 'website_sale_whishlist', ('website_sale',))

    if util.has_enterprise():
        util.remove_module_deps(cr, 'website_helpdesk_livechat', ('helpdesk',))
        util.new_module_dep(cr, 'website_helpdesk_livechat', 'website_helpdesk')

        util.new_module(cr, 'website_studio', ('web_studio', 'website_form_editor'))
