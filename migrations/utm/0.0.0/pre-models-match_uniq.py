# -*- coding: utf-8 -*-

from odoo import models

from odoo.addons.base.maintenance.migrations import util

try:
    from odoo.addons.utm.models import utm_source  # noqa
except ImportError:
    from odoo.addons.utm.models import utm  # noqa


def migrate(cr, version):
    """
    Make sure that there is no utm_{source,medium}_* entry that shares
    the same name with one of the standard xmlids, since restoring the
    standard xmlid would violate the unique_name constraint.
    """
    if util.version_between("saas~15.3", "saas~17.2"):  # 15.3 introduced unique constraint; bump max version if needed
        source_names = [
            ("utm_source_search_engine", "Search engine"),
            ("utm_source_mailing", "Lead Recall"),
            ("utm_source_newsletter", "Newsletter"),
            ("utm_source_facebook", "Facebook"),
            ("utm_source_twitter", "Twitter"),
            ("utm_source_linkedin", "LinkedIn"),
            ("utm_source_monster", "Monster"),
            ("utm_source_glassdoor", "Glassdoor"),
            ("utm_source_craigslist", "Craigslist"),
        ]
        for xmlid, name in source_names:
            util.ensure_xmlid_match_record(cr, "utm." + xmlid, "utm.source", {"name": name})

        medium_names = [
            ("utm_medium_website", "Website"),
            ("utm_medium_phone", "Phone"),
            ("utm_medium_direct", "Direct"),
            ("utm_medium_email", "Email"),
            ("utm_medium_banner", "Banner"),
            ("utm_medium_twitter", "Twitter"),
            ("utm_medium_facebook", "Facebook"),
            ("utm_medium_linkedin", "LinkedIn"),
            ("utm_medium_television", "Television"),
            ("utm_medium_google_adwords", "Google Adwords"),
        ]
        for xmlid, name in medium_names:
            util.ensure_xmlid_match_record(cr, "utm." + xmlid, "utm.medium", {"name": name})


class UtmSource(models.Model):
    _inherit = "utm.source"
    _module = "utm"
    _match_uniq = True
