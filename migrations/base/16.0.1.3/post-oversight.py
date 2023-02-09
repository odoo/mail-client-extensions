from lxml.builder import E

from odoo.upgrade import util


def migrate(cr, version):
    if util.module_installed(cr, "saas_trial"):
        with util.skippable_cm(), util.edit_view(
            cr, "saas_trial.paid_apps_module_kanban", skip_if_not_noupdate=False
        ) as arch:
            elems = arch.xpath("//button[@class='btn btn-primary button_immediate_install' and not(@name)]")
            if elems:
                elems[0].attrib["name"] = "button_immediate_install"
                elems[0].attrib["type"] = "object"

        with util.skippable_cm(), util.edit_view(
            cr, "saas_trial.paid_apps_module_form", skip_if_not_noupdate=False
        ) as arch:
            if not arch.xpath("//field[@name='application']"):
                elems = arch.xpath(
                    """//xpath[@expr="//button[@name='button_immediate_install']" and @position='attributes']"""
                )
                if elems:
                    elem = elems[0]
                    parent = elem.getparent()
                    parent.insert(
                        parent.index(elem),
                        E.xpath(
                            E.field(name="application", invisible="1"),
                            expr="//button[@name='button_immediate_install']",
                            position="after",
                        ),
                    )
