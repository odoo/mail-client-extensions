from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    xml_id_employee = "hr.employee_root"
    xml_id_user = "base.user_root"
    if util.version_gte("saas~11.5"):
        # base.user_root is renamed `base.user_admin` in saas~11.5
        xml_id_user = "base.user_admin"
    if util.version_gte("saas~12.1"):
        # `hr.employee_root` is renamed to `hr.employee_admin` also in saas~11.5
        # but the script doing it `hr/saas~11.5.1.1/pre-10-rename-xmlid.py`is executed after this 0.0.0 script
        # so, on 12.0 upgrade, when this script is executed, it still `hr.employee_root`
        # Upper than 12.0, then it's `hr.employee_admin`
        xml_id_employee = "hr.employee_admin"

    util.ensure_xmlid_match_record(cr, xml_id_employee, "hr.employee", {"user_id": util.ref(cr, xml_id_user)})
