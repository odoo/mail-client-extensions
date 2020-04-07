# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("base.module_category_{communication,sales}_sign"))
    # util.rename_xmlid(cr, *eb("base.module_category_accounting_{invoicing,accounting}"))

    util.remove_record(cr, "base.menu_view_base_language_install")

    util.remove_view(cr, "base.view_company_report_form")
    util.remove_view(cr, "base.view_company_report_form_with_print")

    # users views are loaded after the groups data file (obviously, as views may refer to groups)
    # However, modifying the groups regenerate the view `user_groups_view`, which fail to validate
    # Due to base view being not updated yet. Adapt it to allow passing the validation.
    with util.edit_view(cr, "base.view_users_form", skip_if_not_noupdate=False) as view:
        for node in view.xpath("//field[@name='image']"):
            node.attrib["name"] = "image_128"

    util.force_noupdate(cr, "base.view_users_form", False)
