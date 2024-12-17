from odoo.upgrade import util


def migrate(cr, version):
    script = util.import_script("base/saas~17.2.1.3/pre-30-demo-data.py")
    script.rename_demo_company_xmlids(cr, "lb", from_module_suffix="_account")
    script.rename_demo_company_xmlids(cr, "jo")
