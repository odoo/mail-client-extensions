# -*- coding: utf-8 -*-
from markupsafe import Markup

from odoo.addons.base.models.ir_qweb_fields import nl2br

from odoo.upgrade import util


def migrate(cr, version):
    env = util.env(cr)
    for company in env["res.company"].with_context(active_test=False).search([]):
        # bold layout shouldn't have the company name that is added by default when calling _default_company_details
        # this case is only treated in upgrade so that we don't disrupt existing layouts
        if company.external_report_layout_id.key == env.ref("web.report_layout_bold").view_id.key:
            address_format, company_data = company.partner_id._prepare_display_address(without_company=True)
            company.company_details = Markup(nl2br(address_format)) % company_data
        else:
            company.company_details = env["base.document.layout"].with_company(company)._default_company_details()
