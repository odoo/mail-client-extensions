# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("link_tracker.{view_link_tracker_filter,link_tracker_view_search}"))
    util.rename_xmlid(cr, *eb("link_tracker.{view_link_tracker_form,link_tracker_view_form}"))
    util.rename_xmlid(cr, *eb("link_tracker.{view_link_tracker_tree,link_tracker_view_tree}"))
    util.rename_xmlid(cr, *eb("link_tracker.{link_tracker_view_graph,view_link_tracker_graph}"))
    util.rename_xmlid(cr, *eb("link_tracker.{action_link_tracker,link_tracker_action}"))
    util.rename_xmlid(cr, *eb("link_tracker.{view_link_tracker_click_form,link_tracker_click_view_form}"))
    util.rename_xmlid(cr, *eb("link_tracker.{link_tracker_click_view_tree,view_link_tracker_click_tree}"))
    util.rename_xmlid(cr, *eb("link_tracker.{link_tracker_click_view_graph,view_link_tracker_click_graph}"))
    util.rename_xmlid(cr, *eb("link_tracker.{menu_url_shortener_main,link_tracker_menu_main}"))
