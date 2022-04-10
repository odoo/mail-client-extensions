# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "website.website_visitor_2_1")
    util.remove_column(cr, "website_visitor", "name")
    util.remove_field(cr, "website.visitor", "active")
    util.remove_field(cr, "website.visitor", "parent_id")
    # Token is now either the partner's id or <user-agent+IP> hash.
    # Public visitors (not logged in/linked to a partner) won't be retrieved and
    # will create a new visitor.
    query = """
        UPDATE website_visitor
           SET access_token = partner_id::text
         WHERE partner_id IS NOT NULL
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="website_visitor"))
