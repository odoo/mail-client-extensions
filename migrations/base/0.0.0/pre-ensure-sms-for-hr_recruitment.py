from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.version_between("saas~16.4", "saas~18.1"):
        # There is an action in hr_recruitment that requires sms, the dependencies are wrong
        # it was relying in the autoinstall of sms that could have been uninstalled by clients
        # since we cannot change the dependencies in stable we reinstall sms.
        util.force_install_module(cr, "sms", if_installed=("hr_recruitment",), reason="it's an implicit dependency")
