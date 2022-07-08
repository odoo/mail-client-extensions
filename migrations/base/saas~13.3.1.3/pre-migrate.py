# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    oc = dict(on_collision="merge")
    util.rename_xmlid(cr, *eb("base.module_category_{operations,services}_timesheets"), **oc)
    util.rename_xmlid(cr, *eb("base.module_category_{operations,services}_project"), **oc)
    util.rename_xmlid(cr, *eb("base.module_category_{operations,inventory}_inventory"), **oc)
    util.rename_xmlid(cr, *eb("base.module_category_{operations,inventory}_purchase"), **oc)
    util.rename_xmlid(cr, *eb("base.module_category_{operations,manufacturing}_maintenance"), **oc)
    util.rename_xmlid(cr, *eb("base.module_category_{operations_inventory,inventory}_delivery"), **oc)
    util.rename_xmlid(cr, *eb("base.module_category_{operations,productivity}_documents"), **oc)
    util.rename_xmlid(cr, *eb("base.module_category_{operations,services}_helpdesk"), **oc)
    util.rename_xmlid(cr, *eb("base.module_category_{operations,services}_field_service"), **oc)
    util.rename_xmlid(cr, *eb("base.module_category_manufacturing_{plm,product_lifecycle_management_(plm)}"), **oc)
    util.rename_xmlid(cr, *eb("base.module_category_{localization,accounting_localizations}"), **oc)
    util.rename_xmlid(cr, *eb("base.module_category_sales_{subscription,subscriptions}"), **oc)
    util.rename_xmlid(cr, *eb("base.module_category_marketing_{social,social_marketing}"), **oc)
    util.rename_xmlid(cr, *eb("base.module_category_{accounting,human_resources}_expense"), **oc)
    util.rename_xmlid(cr, *eb("base.module_category_accounting_{payment,payment_acquirers}"), **oc)
    util.rename_xmlid(cr, *eb("base.module_category_{discuss,productivity_discuss}"), **oc)
    util.rename_xmlid(cr, *eb("base.module_category_{,hidden}_tools"), **oc)
    util.rename_xmlid(cr, *eb("base.module_category_{,hidden}_tests"), **oc)

    util.remove_view(cr, "base.view_menu")
    util.remove_view(cr, "base.view_partner_short_form")

    util.remove_record(cr, "base.company_normal_action_tree")
    util.remove_record(cr, "base.action_partner_employee_form")
    util.remove_record(cr, "base.action_partner_other_form")
