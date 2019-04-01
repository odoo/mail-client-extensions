# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # TODO handle demo data
    util.delete_unused(cr, "slide_channel", {"website_slides.channel_partial", "website_slides.channel_private"})

    for role in {"public", "portal", "user"}:
        for model in {"slide", "tag", "channel", "category"}:
            util.remove_record(cr, "website_slides.access_slide_{}_{}".format(model, role))

    # rules
    util.force_noupdate(cr, "website_slides.rule_slide_channel_global", False)
    util.force_noupdate(cr, "website_slides.rule_slide_slide_global", False)

    util.remove_record(cr, "website_slides.rule_slide_channel_public")
    util.remove_record(cr, "website_slides.rule_slide_slide_public")

    # views
    util.rename_xmlid(cr, "website_slides.view_slide_channel_tree", "website_slides.slide_channel_view_tree")
    util.remove_view(cr, "website_slides.channels")
    util.remove_view(cr, "website_slides.opt_subscription_on_channels")
    util.remove_view(cr, "website_slides.channel_not_found")
    util.remove_view(cr, "website_slides.slides_channel_header")
    util.remove_view(cr, "website_slides.home")
    util.remove_view(cr, "website_slides.slides_search")
    util.remove_view(cr, "website_slides.slides_grid_view")
    util.remove_view(cr, "website_slides.slide_detail_view")
    util.remove_view(cr, "website_slides.related_slides")
