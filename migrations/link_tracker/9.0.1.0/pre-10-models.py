# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    if not util.table_exists(cr, 'website_links'):
        return

    util.rename_model(cr, 'website.links', 'link.tracker')
    util.rename_model(cr, 'website.links.click', 'link.tracker.click')
    util.rename_model(cr, 'website.links.code', 'link.tracker.code')

    renames = util.splitlines("""
        {0}.view_{0}_fiter
        {0}.view_{0}_form
        {0}.view_{0}_form_stats
        {0}.action_{0}_stats
        {0}.view_{0}_tree
        {0}.view_{0}_graph
        {0}.action_{0}
        {0}.view_{0}_click_form
        {0}.view_{0}_click_tree
        {0}.view_{0}_click_graph
        {0}.action_{0}_click
    """)
    f, t = 'website_links', 'link_tracker'
    for r in renames:
        util.rename_xmlid(cr, r.format(f), r.format(t))
        util.force_noupdate(cr, r.format(t), False)
