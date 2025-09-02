from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.version_gte("11.0"):
        # For 9.0 to 10.0, there is already
        # hr/9.saas~12.1.1/pre-migrate.py
        # doing a similar job
        _ensure_admin_employee(cr)


def _ensure_admin_employee(cr):
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

    user_id = util.ref(cr, xml_id_user)
    if user_id:
        cr.execute("SELECT id FROM resource_resource WHERE user_id = %s LIMIT 1", [user_id])
        resource_id = cr.fetchone()
        if resource_id:
            (resource_id,) = resource_id
            util.ensure_xmlid_match_record(cr, xml_id_employee, "hr.employee", {"resource_id": resource_id})
