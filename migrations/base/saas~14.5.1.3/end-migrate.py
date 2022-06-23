# -*- coding: utf-8 -*-
from markupsafe import Markup

from odoo.addons.base.models.ir_qweb_fields import nl2br

from odoo.upgrade import util


def migrate(cr, version):
    env = util.env(cr)
    to_report = []

    def set_details(company, ignore_keys=False):
        # bold layout shouldn't have the company name that is added by default when calling _default_company_details
        # this case is only treated in upgrade so that we don't disrupt existing layouts
        if company.external_report_layout_id.key == env.ref("web.report_layout_bold").view_id.key:
            address_format, company_data = company.partner_id.with_context(
                upgrade_ignore_unknown_keys=ignore_keys
            )._prepare_display_address(without_company=True)
            company.company_details = Markup(nl2br(address_format)) % company_data
        else:
            company.company_details = (
                env["base.document.layout"]
                .with_company(company)
                .with_context(upgrade_ignore_unknown_keys=ignore_keys)
                ._default_company_details()
            )

    for company in env["res.company"].with_context(active_test=False).search([]):
        # for some companies the country address format may be using invalid fields
        try:
            set_details(company)
        except KeyError as e:
            to_report.append(
                (
                    company.id,
                    company.name,
                    company.partner_id._get_address_format(),
                    e.args[0],
                    util.get_anchor_link_to_record(env["res.country"], company.partner_id.country_id.id, "View"),
                )
            )
            set_details(company, ignore_keys=True)

    if not to_report:
        return

    message = """
    <details>
    <summary>
        The following companies use invalid fields on their address format. Invalid fields have been ignored during migration.
        Please review the address format in the report settings and correct all invalid fields.
    </summary>
    <ul>
        {}
    </ul>
    </details>
    """.format(
        "\n".join(
            f"<li>'{util.html_escape(name)}' (with id={id}) has address format `{util.html_escape(aformat)}` using "
            f"(at least) the invalid field '{util.html_escape(field)}' [{link}].</li>"
            for id, name, aformat, field, link in to_report
        )
    )
    util.add_to_migration_reports(category="Company addresses", format="html", message=message)
