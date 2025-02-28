from odoo.upgrade import util


def migrate(cr, version):
    env = util.env(cr)
    user = env["res.users"].browse(util.ref(cr, "base.default_user"))
    default_group_id = util.ref(cr, "base.default_user_group")
    env["res.groups"].browse(default_group_id).write(
        {
            "implied_ids": [(6, 0, (user.group_ids - user.group_ids.implied_ids.all_implied_ids).ids)],
        }
    )

    util.update_record_from_xml(cr, "base.ir_filters_employee_rule")
    util.update_record_from_xml(cr, "base.europe", force_create=False, fields=["code"])
    util.update_record_from_xml(cr, "base.south_america", force_create=False, fields=["code"])
    util.update_record_from_xml(cr, "base.sepa_zone", force_create=False, fields=["code"])
    util.update_record_from_xml(cr, "base.gulf_cooperation_council", force_create=False, fields=["code"])
    util.update_record_from_xml(cr, "base.eurasian_economic_union", force_create=False, fields=["code"])
    util.update_record_from_xml(cr, "base.ch_and_li", force_create=False, fields=["code"])
    util.update_record_from_xml(cr, "base.dom-tom", force_create=False, fields=["code"])

    # updating only sequence
    util.update_record_from_xml(cr, "base.module_category_supply_chain", fields=["sequence"])
    util.update_record_from_xml(cr, "base.module_category_hidden", fields=["sequence"])
    util.update_record_from_xml(cr, "base.module_category_accounting", fields=["sequence"])
    util.update_record_from_xml(cr, "base.module_category_website", fields=["sequence"])
    util.update_record_from_xml(cr, "base.module_category_services", fields=["sequence"])
    util.update_record_from_xml(cr, "base.module_category_productivity", fields=["sequence"])
