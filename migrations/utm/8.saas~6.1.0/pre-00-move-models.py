# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if not util.module_installed(cr, "crm"):
        return
    for model in "medium campaign source mixin".split():
        rename_table = model != "mixin"  # because it's an abstract model
        util.rename_model(cr, "crm.tracking.%s" % model, "utm.%s" % model, rename_table)
        util.move_model(cr, "utm.%s" % model, "crm", "utm", move_data=True)

    xids = """
        {crm,utm}_source_search_engine
        {crm,utm}_source_mailing
        {crm,utm}_source_newsletter
        {crm,utm}_medium_website
        {crm,utm}_medium_phone
        {crm,utm}_medium_direct
        {crm,utm}_medium_email
        {crm,utm}_medium_banner

        {crm_tracking,utm}_campaign_tree
        {crm_tracking,utm}_campaign_form
        {crm_tracking,utm}_campaign_act
        menu_{crm_tracking,utm}_campaign_act
        {crm_tracking,utm}_medium_view_tree
        {crm_tracking,utm}_medium_view_form
        {crm_tracking,utm}_medium_action
        {crm_tracking,utm}_source_view_tree
        {crm_tracking,utm}_source_view_form
        {crm_tracking,utm}_source_action
        menu_{crm_tracking,utm}_source
    """

    for m in util.splitlines(xids):
        util.rename_xmlid(cr, *util.expand_braces("utm." + m))
