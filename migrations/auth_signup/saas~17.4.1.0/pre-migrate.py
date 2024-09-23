from odoo.upgrade import util


def migrate(cr, version):
    # replace the usage of `signup_url` in mail templates
    replacements = [
        ("user_id", ".partner_id", "res.users"),
        ("partner_id", "", "res.partner"),
    ]
    for varname, subfield, model in replacements:
        util.replace_in_all_jsonb_values(
            cr,
            "mail_template",
            "body_html",
            f"{varname}.signup_url",
            f"{varname}{subfield}._get_signup_url()",
        )
        util.replace_in_all_jsonb_values(
            cr,
            "mail_template",
            "body_html",
            "object.signup_url",
            f"object{subfield}._get_signup_url()",
            extra_filter=cr.mogrify("t.model = %s", [model]).decode(),
        )

    # bare replacement for other cases, asuming they are on `res.users`.
    util.replace_in_all_jsonb_values(cr, "mail_template", "body_html", ".signup_url", ".partner_id._get_signup_url()")

    util.remove_field(cr, "res.partner", "signup_url")
    util.remove_field(cr, "res.partner", "signup_valid")
    util.remove_field(cr, "res.partner", "signup_token")
    util.remove_field(cr, "res.partner", "signup_expiration")
