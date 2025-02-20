from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~18.2")
class TestMigrateRecruitmentSkill(UpgradeCase):
    def prepare(self):
        # Find the candidates from TestMigrateRecruitment.
        # We can't create new candidates here because those will break the tests in TestMigrateRecruitment.
        no_app_cand = self.env["hr.candidate"].search(
            [
                ("partner_name", "=", "NoAppCandidate"),
                ("partner_phone", "=", "1234"),
                ("email_from", "=", "NoAppCandidate@example.com"),
                ("linkedin_profile", "=", "linkedin.NoAppCandidate"),
            ]
        )
        one_app_cand = self.env["hr.candidate"].search(
            [
                ("partner_name", "=", "OneAppCandidate"),
                ("partner_phone", "=", "2345"),
                ("email_from", "=", "OneAppCandidate@example.com"),
                ("linkedin_profile", "=", "linkedin.OneAppCandidate"),
            ]
        )
        multi_app_cand = self.env["hr.candidate"].search(
            [
                ("partner_name", "=", "MultiAppCandidate"),
                ("partner_phone", "=", "3456"),
                ("email_from", "=", "MultiAppCandidate@example.com"),
                ("linkedin_profile", "=", "linkedin.MultiAppCandidate"),
            ]
        )

        nac_skill_1, nac_skill_2, nac_skill_3, oac_skill_1, mac_skill_1, mac_skill_2 = self.env[
            "hr.candidate.skill"
        ].create(
            [
                {
                    "candidate_id": no_app_cand.id,
                    "skill_id": self.env.ref("hr_skills.hr_skill_french").id,
                    "skill_level_id": self.env.ref("hr_skills.hr_skill_level_a1").id,
                    "skill_type_id": self.env.ref("hr_skills.hr_skill_type_lang").id,
                },
                {
                    "candidate_id": no_app_cand.id,
                    "skill_id": self.env.ref("hr_skills.hr_skill_spanish").id,
                    "skill_level_id": self.env.ref("hr_skills.hr_skill_level_b2").id,
                    "skill_type_id": self.env.ref("hr_skills.hr_skill_type_lang").id,
                },
                {
                    "candidate_id": no_app_cand.id,
                    "skill_id": self.env.ref("hr_skills.hr_skill_teamwork").id,
                    "skill_level_id": self.env.ref("hr_skills.hr_skill_level_elementary_softskill").id,
                    "skill_type_id": self.env.ref("hr_skills.hr_skill_type_softskill").id,
                },
                {
                    "candidate_id": one_app_cand.id,
                    "skill_id": self.env.ref("hr_skills.hr_skill_spanish").id,
                    "skill_level_id": self.env.ref("hr_skills.hr_skill_level_b1").id,
                    "skill_type_id": self.env.ref("hr_skills.hr_skill_type_lang").id,
                },
                {
                    "candidate_id": multi_app_cand.id,
                    "skill_id": self.env.ref("hr_skills.hr_skill_spanish").id,
                    "skill_level_id": self.env.ref("hr_skills.hr_skill_level_b2").id,
                    "skill_type_id": self.env.ref("hr_skills.hr_skill_type_lang").id,
                },
                {
                    "candidate_id": multi_app_cand.id,
                    "skill_id": self.env.ref("hr_skills.hr_skill_french").id,
                    "skill_level_id": self.env.ref("hr_skills.hr_skill_level_c1").id,
                    "skill_type_id": self.env.ref("hr_skills.hr_skill_type_lang").id,
                },
            ]
        )
        return {
            "oac_app": one_app_cand.applicant_ids.id,
            "mac_apps": multi_app_cand.applicant_ids.ids,
            "nac_skills": [nac_skill_1.id, nac_skill_2.id, nac_skill_3.id],
            "oac_skills": oac_skill_1.id,
            "mac_skills": [mac_skill_1.id, mac_skill_2.id],
        }

    def check(self, init):
        no_app_cand_talent = self.env["hr.applicant"].search(
            [
                ("partner_name", "=", "NoAppCandidate"),
                ("partner_phone", "=", "1234"),
                ("email_from", "=", "noappcandidate@example.com"),
                ("linkedin_profile", "=", "linkedin.NoAppCandidate"),
                ("job_id", "=", False),
            ]
        )

        multi_app_cand_talent = self.env["hr.applicant"].search(
            [
                ("partner_name", "=", "MultiAppCandidate"),
                ("partner_phone", "=", "3456"),
                ("email_from", "=", "multiappcandidate@example.com"),
                ("linkedin_profile", "=", "linkedin.MultiAppCandidate"),
                ("job_id", "=", False),
            ]
        )

        # Make sure the skills transferred properply from the candidate to the talent or the single application.
        self.assertCountEqual(
            no_app_cand_talent.applicant_skill_ids.ids,
            init["nac_skills"],
            "The skills should have been moved from the candidate NoAppCandidate to the applicant('talent')",
        )

        oac_application = self.env["hr.applicant"].browse(init["oac_app"])
        self.assertEqual(
            oac_application.applicant_skill_ids.id,
            init["oac_skills"],
            "The skills should have been moved from the candidate OneAppCandidate to the applicant",
        )
        self.assertCountEqual(
            multi_app_cand_talent.applicant_skill_ids.ids,
            init["mac_skills"],
            "The skills should have been moved from the candidate MultiAppCandidate to the applicant('talent')",
        )

        # Make sure the skills were duplicated for each application of the multi app candidate
        mac_applications = self.env["hr.applicant"].browse(init["mac_apps"])
        mac_talent_skills = {
            (skill.skill_id.name, skill.skill_level_id.name) for skill in multi_app_cand_talent.applicant_skill_ids
        }
        for applicant in mac_applications:
            applicant_skills = {
                (skill.skill_id.name, skill.skill_level_id.name) for skill in applicant.applicant_skill_ids
            }
            self.assertSetEqual(
                applicant_skills,
                mac_talent_skills,
                f"Application {applicant.id} does not have the same skills as the talent 'MultiAppCandidate'",
            )
