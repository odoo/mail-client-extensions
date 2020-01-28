# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # When updating translations of a `translate=xml_translate` field, the ORM tries to match
    # existing terms (with a small percentage of differences) to avoid losing existing translations.
    # However, for this view, the terms are similar enough to be kept but not up to date as they
    # do not contain an XML attribute used as an XPath hook point in an inherited view.
    # Force update of these translations to avoid generating an unapplicable view in other languages.
    # See https://github.com/odoo/saas-migration/issues/714
    cr.execute(
        "DELETE FROM ir_translation WHERE name = 'ir.ui.view,arch_db' AND res_id = %s",
        [util.ref(cr, "mail.email_compose_message_wizard_form")],
    )
