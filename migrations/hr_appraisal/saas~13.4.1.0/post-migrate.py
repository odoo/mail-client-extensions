# -*- coding: utf-8 -*-

from odoo.addons.hr_appraisal.__init__ import _generate_assessment_note_ids

from odoo.upgrade import util


def migrate(cr, version):
    # Force the post_init_hook configuration
    _generate_assessment_note_ids(cr, False)  # noqa: FBT003

    util.update_record_from_xml(cr, "hr_appraisal.hr_appraisal_rule_base_user")
    # Force noupdate data update (in post, otherwise hr.appraisal.plan not in registry)
    util.update_record_from_xml(cr, "hr_appraisal.ir_cron_scheduler_appraisal")
