from odoo.upgrade import util


def migrate(cr, version):
    if util.module_installed(cr, "saas_trial"):
        with util.skippable_cm(), util.edit_view(
            cr, "saas_trial.application_field_access", skip_if_not_noupdate=False, active=None
        ) as arch:
            for elem in arch.xpath("//xpath[@position='after']"):
                if elem.get("expr") == "//div[hasclass('oe_title')]/div":
                    elem.set("expr", "//page[@name='technical_data']")
