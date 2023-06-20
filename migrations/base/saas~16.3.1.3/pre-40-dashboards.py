# -*- coding: utf-8 -*-
import re
from html import unescape

from odoo.upgrade.util.helpers import _dashboard_actions


def migrate(cr, version):
    entities = ("&#x27;", "&#x60;", "&quot;", "&amp;", "&lt;", "&gt;")
    match = "|".join(re.escape(e) for e in entities)

    for _, act in _dashboard_actions(cr, match):
        domain = act.get("domain")
        if domain and any(entity in domain for entity in entities):
            act.set("domain", unescape(domain))
