# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("base.module_category_{operations,services}_timesheets"))
    util.rename_xmlid(cr, *eb("base.module_category_{operations,services}_project"))
    util.rename_xmlid(cr, *eb("base.module_category_{operations,inventory}_inventory"))
    util.rename_xmlid(cr, *eb("base.module_category_{operations,inventory}_purchase"))
    util.rename_xmlid(cr, *eb("base.module_category_{operations,manufacturing}_maintenance"))
    util.rename_xmlid(cr, *eb("base.module_category_{operations_inventory,inventory}_delivery"))
    util.rename_xmlid(cr, *eb("base.module_category_{operations,productivity}_documents"))
    util.rename_xmlid(cr, *eb("base.module_category_{operations,services}_helpdesk"))
    util.rename_xmlid(cr, *eb("base.module_category_{operations,services}_field_service"))
    util.rename_xmlid(cr, *eb("base.module_category_manufacturing_{plm,product_lifecycle_management_(plm)}"))
    util.rename_xmlid(cr, *eb("base.module_category_{localization,accounting_localizations}"))
    util.rename_xmlid(cr, *eb("base.module_category_sales_{subscription,subscriptions}"))
    util.rename_xmlid(cr, *eb("base.module_category_marketing_{social,social_marketing}"))
    util.rename_xmlid(cr, *eb("base.module_category_{tools,hidden_tools}"))
    util.rename_xmlid(cr, *eb("base.module_category_{tests,hidden_tests}"))
    util.rename_xmlid(cr, *eb("base.module_category_{accounting,human_resources}_expense"))
    util.rename_xmlid(cr, *eb("base.module_category_accounting_{payment,payment_acquirers}"))
    util.rename_xmlid(cr, *eb("base.module_category_{discuss,productivity_discuss}"))
