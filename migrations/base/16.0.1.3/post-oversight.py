from odoo.upgrade import util


def migrate(cr, version):
    if util.module_installed(cr, "saas_trial"):
        with util.skippable_cm(), util.edit_view(cr, "saas_trial.paid_apps_module_kanban") as arch:
            elems = arch.xpath("//button[@class='btn btn-primary button_immediate_install' and not(@name)]")
            if elems:
                elems[0].attrib["name"] = "button_immediate_install"
