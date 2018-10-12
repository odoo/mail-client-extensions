# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    eb = util.expand_braces
    types = "signature initial text multiline_text date name email phone company".split()
    for t in types:
        util.rename_xmlid(cr, *eb("sign.sign{ature,}_item_type_" + t))

    roles = "customer company employee".split()
    for r in roles:
        util.rename_xmlid(cr, *eb("sign.{signature_item_party,sign_item_role}_" + r))

    for c in {1, 3}:
        util.rename_xmlid(cr, *eb("sign.attachment_{website_,}sign_%s" % c))
        util.rename_xmlid(cr, *eb("sign.template_{website_,}sign_%s" % c))

    for i in {1, 2, 3, 4, 5, 8, 9, 20, 21, 22, 23, 24, 25}:
        util.rename_xmlid(cr, *eb("sign.sign{ature,}_item_%s" % i))

    models = util.splitlines(
        """
        sign{ature,}_request
        sign{ature_request,}_template
        sign{ature,}_request_item
        sign{ature,}_item
        sign{ature,}_item_value
        sign{ature_item_party,_item_role}
        sign{ature,}_item_type
    """
    )
    for model in models:
        util.rename_xmlid(cr, *eb("sign.access_%s_all" % model))
        util.rename_xmlid(cr, *eb("sign.access_%s_group_user" % model))

    util.rename_xmlid(cr, *eb("sign.group_{website_,}sign_user"))
    util.rename_xmlid(cr, *eb("sign.group_{website_,}sign_manager"))

    rules = util.splitlines(
        """
        ir_rule_sign{ature_request,}_template_group_website_sign_user
        ir_rule_sign{ature_request,}_template_group_website_sign_manager

        ir_rule_sign{ature,}_request_group_website_sign_user_create
        ir_rule_sign{ature,}_request_group_website_sign_user_modify
        ir_rule_sign{ature,}_request_group_website_sign_manager
    """
    )
    for rule in rules:
        f, t = eb("sign." + rule)
        util.rename_xmlid(cr, f, t.replace("website_", ""))

    renames = util.splitlines(
        """
        sign{ature,}_request_view_kanban
        sign{ature,}_request_view_tree
        sign{ature,}_request_view_form
        sign{ature,}_request_view_search
        sign{ature,}_request_action

        sign{ature,}_request_item_view_tree
        sign{ature,}_request_item_view_form

        sign{ature_request,}_template_view_kanban
        sign{ature_request,}_template_view_tree
        sign{ature_request,}_template_view_form
        sign{ature_request,}_template_view_search
        sign{ature_request,}_template_action
        sign{ature_request,}_template_with_archived_action
        sign{ature_request,}_template_menu

        sign{ature,}_item_view_tree
        sign{ature,}_item_view_form

        sign{ature,}_item_type_view_tree
        sign{ature,}_item_type_view_form
        sign{ature,}_item_type_action
        sign{ature,}_item_type_menu

        sign{ature_item_party,_item_role}_view_tree
        sign{ature_item_party,_item_role}_view_form
        sign{ature_item_party,_item_role}_action
        sign{ature_item_party,_item_role}_menu
    """
    )
    for rename in renames:
        util.rename_xmlid(cr, *eb("sign." + rename))
