# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):

    # website.layout changed in an incompatible manner at fe3775b and
    # will always be forced-reset, so we need to reset this one too,
    # as it inherits from a different template now!
    # Theoretically it only adds a small "News" link in the footer,
    # so customizations are unlikely.
    util.force_noupdate(cr, 'website_blog.header_footer_custom', False)

    # force update of view
    util.force_noupdate(cr, 'website_blog.blog_post_complete', False)

    # Pre-delete incompatible views, would be deleted anyway at the end
    util.remove_record(cr, 'website_blog.opt_blog_post_complete_author')
    util.remove_record(cr, 'website_blog.opt_blog_post_complete_blog')
