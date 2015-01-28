# -*- coding: utf-8 -*-
import re
from openerp.addons.base.maintenance.migrations import util

def expand_braces(s):
    # expand braces (a la bash)
    # only handle one expension of a 2 parts (because we don't need more)
    r = re.compile(r'(.*){([^},]*?,[^},]*?)}(.*)')
    m = r.search(s)
    if not m:
        raise ValueError('no braces to expand')
    head, match, tail = m.groups()
    a, b = match.split(',')
    return [head + a + tail, head + b + tail]

def migrate(cr, version):
    for model in 'medium campaign source mixin'.split():
        rename_table = model != 'mixin'     # because it's an abstract model
        util.rename_model(cr, 'crm.tracking.%s' % model, 'utm.%s' % model, rename_table)
        util.move_model(cr, 'utm.%s' % model, 'crm', 'utm', move_data=True)

    xids = filter(None, """
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
    """.strip().split())

    for m in xids:
        util.rename_xmlid(cr, *expand_braces('utm.' + m))
