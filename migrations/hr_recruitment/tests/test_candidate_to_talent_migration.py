from datetime import date

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~18.2")
class TestMigrateRecruitment(UpgradeCase):
    def prepare(self):
        other_company = self.env["res.company"].create({"name": "Other Company"})
        default_company = self.env.ref("base.main_company")
        department_main, department_other = self.env["hr.department"].create(
            [
                {"name": "DefaultUpgradeDepartment", "company_id": default_company.id},
                {"name": "OtherUpgradeDepartment", "company_id": other_company.id},
            ]
        )

        job_1, job_2, job_3, job_4 = self.env["hr.job"].create(
            [
                {"name": "job_1", "department_id": department_main.id, "company_id": default_company.id},
                {"name": "job_2", "department_id": department_main.id, "company_id": default_company.id},
                {"name": "job_3", "department_id": department_main.id, "company_id": default_company.id},
                {"name": "job_4", "department_id": department_other.id, "company_id": other_company.id},
            ]
        )

        (
            _no_app_cand,
            one_app_cand,
            multi_app_cand,
            _no_app_no_comp_cand,
            one_app_no_comp_cand,
            multi_app_no_comp_cand,
            _no_app_other_comp_cand,
            one_app_other_comp_cand,
            multi_app_other_comp_cand,
        ) = self.env["hr.candidate"].create(
            [
                {
                    "partner_name": "NoAppCandidate",
                    "partner_phone": "1234",
                    "email_from": "NoAppCandidate@example.com",
                    "linkedin_profile": "linkedin.NoAppCandidate",
                    "company_id": default_company.id,
                },
                {
                    "partner_name": "OneAppCandidate",
                    "partner_phone": "2345",
                    "email_from": "OneAppCandidate@example.com",
                    "linkedin_profile": "linkedin.OneAppCandidate",
                    "availability": date(2024, 12, 19),
                    "color": 3,
                    "type_id": 1,
                    "company_id": default_company.id,
                },
                {
                    "partner_name": "MultiAppCandidate",
                    "partner_phone": "3456",
                    "email_from": "MultiAppCandidate@example.com",
                    "linkedin_profile": "linkedin.MultiAppCandidate",
                    "availability": date(2025, 4, 1),
                    "color": 4,
                    "type_id": 2,
                    "company_id": default_company.id,
                },
                {
                    "partner_name": "NoAppNoCompCandidate",
                    "partner_phone": "4567",
                    "email_from": " NoAppNoCompCandidate@example.com",
                    "linkedin_profile": "linkedin.NoAppNoCompCandidate",
                    "company_id": False,
                },
                {
                    "partner_name": "OneAppNoCompCandidate",
                    "partner_phone": "5678",
                    "email_from": "OneAppNoCompCandidate@example.com",
                    "linkedin_profile": "linkedin.OneAppNoCompCandidate",
                    "company_id": False,
                },
                {
                    "partner_name": "MultiAppNoCompCandidate",
                    "partner_phone": "6789",
                    "email_from": "MultiAppNoCompCandidate@example.com",
                    "linkedin_profile": "linkedin.MultiAppNoCompCandidate",
                    "company_id": False,
                },
                {
                    "partner_name": "NoAppOtherCompCandidate",
                    "partner_phone": "7890",
                    "email_from": " NoAppOtherCompCandidate@example.com",
                    "linkedin_profile": "linkedin.NoAppOtherCompCandidate",
                    "company_id": other_company.id,
                },
                {
                    "partner_name": "OneAppOtherCompCandidate",
                    "partner_phone": "8901",
                    "email_from": " OneAppOtherCompCandidate@example.com",
                    "linkedin_profile": "linkedin.OneAppOtherCompCandidate",
                    "company_id": other_company.id,
                },
                {
                    "partner_name": "MultiAppOtherCompCandidate",
                    "partner_phone": "9012",
                    "email_from": "MultiAppOtherCompCandidate@example.com",
                    "linkedin_profile": "linkedin.MultiAppOtherCompCandidate",
                    "company_id": other_company.id,
                },
            ]
        )
        (
            oac_app,
            mac_app_1,
            mac_app_2,
            mac_app_3,
            oancc_app,
            mancc_app_1,
            mancc_app_2,
            oaocc_app,
            maocc_app_1,
            maocc_app_2,
        ) = self.env["hr.applicant"].create(
            [
                {"candidate_id": one_app_cand.id, "job_id": job_1.id},
                {"candidate_id": multi_app_cand.id, "job_id": job_1.id},
                {"candidate_id": multi_app_cand.id, "job_id": job_2.id},
                {"candidate_id": multi_app_cand.id, "job_id": job_3.id},
                {
                    "candidate_id": one_app_no_comp_cand.id,
                    "job_id": job_1.id,
                    "company_id": False,
                },
                {
                    "candidate_id": multi_app_no_comp_cand.id,
                    "job_id": job_1.id,
                    "company_id": False,
                },
                {
                    "candidate_id": multi_app_no_comp_cand.id,
                    "job_id": job_1.id,
                    "company_id": False,
                },
                {
                    "candidate_id": one_app_other_comp_cand.id,
                    "job_id": job_4.id,
                    "company_id": other_company.id,
                },
                {
                    "candidate_id": multi_app_other_comp_cand.id,
                    "job_id": job_4.id,
                    "company_id": other_company.id,
                },
                {
                    "candidate_id": multi_app_other_comp_cand.id,
                    "job_id": job_4.id,
                    "company_id": other_company.id,
                },
            ]
        )
        return {
            "oac_app": oac_app.id,
            "mac_apps": [
                mac_app_1.id,
                mac_app_2.id,
                mac_app_3.id,
            ],
            "oancc_app": oancc_app.id,
            "mancc_apps": [mancc_app_1.id, mancc_app_2.id],
            "oaocc_app": oaocc_app.id,
            "maocc_apps": [
                maocc_app_1.id,
                maocc_app_2.id,
            ],
            "main_company_id": default_company.id,
            "main_company_name": default_company.name,
            "other_company_id": other_company.id,
        }

    def check(self, init):
        # ---
        # Talent Pool creations
        # ---

        main_comp_talent_pool = self.env["hr.talent.pool"].search(
            [
                ("company_id", "=", init["main_company_id"]),
                ("name", "=", f"Candidates for company {init['main_company_name']}"),
            ]
        )
        other_comp_talent_pool = self.env["hr.talent.pool"].search([("company_id", "=", init["other_company_id"])])
        no_comp_talent_pool = self.env["hr.talent.pool"].search([("company_id", "=", False)])

        self.assertTrue(main_comp_talent_pool, "A talent pool should be created for the main company")
        self.assertTrue(other_comp_talent_pool, "A talent pool should be created for the other company")
        self.assertFalse(no_comp_talent_pool, "A talent pool should NOT be created for the other company")

        self.assertEqual(other_comp_talent_pool.name, "Candidates for company Other Company")
        self.assertTrue(
            {"NoAppCandidate", "MultiAppCandidate"}.issubset(
                set(main_comp_talent_pool.talent_ids.mapped("partner_name"))
            ),
            "The Talent Pool for 'YourCompany' should contain a talent for the NoAppCandidate and the MultiAppCandidate",
        )
        self.assertFalse(
            {"NoAppOtherCompCandidate", "MultiAppOtherCompCandidate"}.issubset(
                set(main_comp_talent_pool.talent_ids.mapped("partner_name"))
            ),
            "The Talent Pool for 'YourCompany' should NOT contain a talent for the NoAppOtherCompCandidate and the MultiAppOtherCompCandidate",
        )
        self.assertTrue(
            {"NoAppOtherCompCandidate", "MultiAppOtherCompCandidate"}.issubset(
                other_comp_talent_pool.talent_ids.mapped("partner_name")
            ),
            "The Talent Pool for 'Other Company' should contain a talent for the NoAppOtherCompCandidate and the MultiAppOtherCompCandidate",
        )

        self.assertFalse(
            {"NoAppCandidate", "MultiAppCandidate"}.issubset(other_comp_talent_pool.talent_ids.mapped("partner_name")),
            "The Talent Pool for 'Other Company' should NOT contain a talent for the NoAppCandidate and the MultiAppCandidate",
        )
        # ---
        # Talent creation
        # ---
        # Base company all cases

        no_app_cand_talent = self.env["hr.applicant"].search(
            [
                ("partner_name", "=", "NoAppCandidate"),
                ("partner_phone", "=", "1234"),
                ("email_from", "=", "noappcandidate@example.com"),
                ("linkedin_profile", "=", "linkedin.NoAppCandidate"),
                ("job_id", "=", False),
            ]
        )
        self.assertTrue(
            no_app_cand_talent,
            "An applicant('talent') should have been created for the NoAppCandidate",
        )
        self.assertEqual(
            main_comp_talent_pool.id,
            no_app_cand_talent.talent_pool_ids.id,
            "The Application('talent') for the NoAppCandidate should be linked to the candidates talent pool",
        )

        one_app_cand_talent = self.env["hr.applicant"].search(
            [
                ("partner_name", "=", "OneAppCandidate"),
                ("partner_phone", "=", "2345"),
                ("email_from", "=", "oneappcandidate@example.com"),
                ("linkedin_profile", "=", "linkedin.OneAppCandidate"),
                ("job_id", "=", False),
            ]
        )
        self.assertFalse(
            one_app_cand_talent,
            "An applicant('talent') should NOT have been created for the OneAppCandidate",
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
        self.assertTrue(
            multi_app_cand_talent, "An applicant('talent') should have been created for the MultiAppCandidate"
        )
        self.assertEqual(
            main_comp_talent_pool.id,
            multi_app_cand_talent.talent_pool_ids.id,
            "The Application('talent') for the MultiAppCandidate should be linked to the candidates talent pool",
        )

        # No company all cases

        no_app_no_comp_cand_talent = self.env["hr.applicant"].search(
            [
                ("partner_name", "=", "NoAppNoCompCandidate"),
                ("partner_phone", "=", "4567"),
                ("email_from", "=", "noappnocompcandidate@example.com"),
                ("linkedin_profile", "=", "linkedin.NoAppNoCompCandidate"),
                ("job_id", "=", False),
            ]
        )
        self.assertTrue(
            no_app_no_comp_cand_talent,
            "An applicant('talent') should have been created for the NoAppNoCompCandidate",
        )
        self.assertFalse(
            no_app_no_comp_cand_talent.talent_pool_ids,
            "The applicant('talet') for NoAppNoCompCandidate should not be linked to any talent pool",
        )

        one_app_no_comp_cand_talent = self.env["hr.applicant"].search(
            [
                ("partner_name", "=", "OneAppNoCompCandidate"),
                ("partner_phone", "=", "5678"),
                ("email_from", "=", "oneappnocompcandidate@example.com"),
                ("linkedin_profile", "=", "linkedin.OneAppNoCompCandidate"),
                ("job_id", "=", False),
            ]
        )
        self.assertFalse(
            one_app_no_comp_cand_talent,
            "An applicant('talent') should NOT have been created for the OneAppNoCompCandidate",
        )

        multi_app_no_comp_cand_talent = self.env["hr.applicant"].search(
            [
                ("partner_name", "=", "MultiAppNoCompCandidate"),
                ("partner_phone", "=", "6789"),
                ("email_from", "=", "multiappnocompcandidate@example.com"),
                ("linkedin_profile", "=", "linkedin.MultiAppNoCompCandidate"),
                ("job_id", "=", False),
            ]
        )
        self.assertTrue(
            multi_app_no_comp_cand_talent,
            "An applicant('talent') should have been created for the MultiAppNoCompCandidate",
        )
        self.assertFalse(
            multi_app_no_comp_cand_talent.talent_pool_ids,
            "The applicant('talet') for MultiAppNoCompCandidate should not be linked to any talent pool",
        )

        # Other company all cases

        no_app_other_comp_cand_talent = self.env["hr.applicant"].search(
            [
                ("partner_name", "=", "NoAppOtherCompCandidate"),
                ("partner_phone", "=", "7890"),
                ("email_from", "=", "noappothercompcandidate@example.com"),
                ("linkedin_profile", "=", "linkedin.NoAppOtherCompCandidate"),
                ("job_id", "=", False),
            ]
        )
        self.assertTrue(
            no_app_other_comp_cand_talent,
            "An applicant('talent') should have been created for the NoAppOtherCompCandidate",
        )
        self.assertEqual(
            other_comp_talent_pool.id,
            no_app_other_comp_cand_talent.talent_pool_ids.id,
            "The Application('talent') for the NoAppOtherCompCandidate should be linked to the candidates talent pool",
        )

        one_app_other_comp_cand_talent = self.env["hr.applicant"].search(
            [
                ("partner_name", "=", "OneAppOtherCompCandidate"),
                ("partner_phone", "=", "8901"),
                ("email_from", "=", "OneAppOtherCompCandidate@example.com"),
                ("linkedin_profile", "=", "linkedin.OneAppOtherCompCandidate"),
                ("job_id", "=", False),
            ]
        )
        self.assertFalse(
            one_app_other_comp_cand_talent,
            "An applicant('talent') should NOT have been created for the OneAppOtherCompCandidate",
        )

        multi_app_other_comp_cand_talent = self.env["hr.applicant"].search(
            [
                ("partner_name", "=", "MultiAppOtherCompCandidate"),
                ("partner_phone", "=", "9012"),
                ("email_from", "=", "multiappothercompcandidate@example.com"),
                ("linkedin_profile", "=", "linkedin.MultiAppOtherCompCandidate"),
                ("job_id", "=", False),
            ]
        )
        self.assertTrue(
            multi_app_other_comp_cand_talent,
            "An applicant('talent') should have been created for the MultiAppOtherCompCandidate",
        )

        self.assertEqual(
            other_comp_talent_pool.id,
            multi_app_other_comp_cand_talent.talent_pool_ids.id,
            "The Application('talent') for the MultiAppOtherCompCandidate should be linked to the candidates talent pool",
        )

        # ---
        # Application creation and information transfer
        # ---
        # base company all cases

        nac_app = self.env["hr.applicant"].search_count(
            [
                ("partner_name", "=", "NoAppCandidate"),
                ("partner_phone", "=", "1234"),
                ("email_from", "=", "noappcandidate@example.com"),
                ("linkedin_profile", "=", "linkedin.NoAppCandidate"),
            ]
        )
        self.assertEqual(
            nac_app,
            1,
            "There should only be 1 application, the talent, for NoAppCandidate",
        )

        oac_application = self.env["hr.applicant"].browse(init["oac_app"])
        self.assertTrue(oac_application, "The Application for OneAppCandidate should still exists")
        oac_app_data = {
            "partner_name": oac_application.partner_name,
            "partner_phone": oac_application.partner_phone,
            "email_from": oac_application.email_from,
            "linkedin_profile": oac_application.linkedin_profile,
            "availability": oac_application.availability,
            "color": oac_application.color,
            "type_id": oac_application.type_id.id,
            "company_id": oac_application.company_id.id,
        }

        self.assertDictEqual(
            {
                "partner_name": "OneAppCandidate",
                "partner_phone": "2345",
                "email_from": "oneappcandidate@example.com",
                "linkedin_profile": "linkedin.OneAppCandidate",
                "availability": date(2024, 12, 19),
                "color": 3,
                "type_id": 1,
                "company_id": init["main_company_id"],
            },
            oac_app_data,
            "The information from OneAppCandidate should have transferred from the candidate to the applicant",
        )

        mac_applications = self.env["hr.applicant"].browse(init["mac_apps"])

        self.assertCountEqual(
            init["mac_apps"],
            mac_applications.ids,
            "The Application for MultiAppCandidate should still exists",
        )
        mac_app_data = {
            "partner_name": set(mac_applications.mapped("partner_name")),
            "partner_phone": set(mac_applications.mapped("partner_phone")),
            "email_from": set(mac_applications.mapped("email_from")),
            "linkedin_profile": set(mac_applications.mapped("linkedin_profile")),
            "availability": set(mac_applications.mapped("availability")),
            "color": set(mac_applications.mapped("color")),
            "type_id": set(mac_applications.mapped("type_id.id")),
            "company_id": set(mac_applications.mapped("company_id.id")),
        }
        self.assertDictEqual(
            {
                "partner_name": {"MultiAppCandidate"},
                "partner_phone": {"3456"},
                "email_from": {"multiappcandidate@example.com"},
                "linkedin_profile": {"linkedin.MultiAppCandidate"},
                "availability": {date(2025, 4, 1)},
                "color": {4},
                "type_id": {2},
                "company_id": {init["main_company_id"]},
            },
            mac_app_data,
            "The information from MultiAppCandidate should have transferred from the candidate to all of the applicants",
        )

        # No company all cases

        nancc_app = self.env["hr.applicant"].search_count(
            [
                ("partner_name", "=", "NoAppNoCompCandidate"),
                ("partner_phone", "=", "4567"),
                ("email_from", "=", "noappnocompcandidate@example.com"),
                ("linkedin_profile", "=", "linkedin.NoAppNoCompCandidate"),
            ]
        )
        self.assertEqual(
            nancc_app,
            1,
            "There should only be 1 application, the talent, for NoAppNoCompCandidate",
        )

        oancc_application = self.env["hr.applicant"].browse(init["oancc_app"])
        self.assertTrue(oancc_application, "The Application for OneAppNoCompCandidate should still exists")
        oancc_app_data = {
            "partner_name": oancc_application.partner_name,
            "partner_phone": oancc_application.partner_phone,
            "email_from": oancc_application.email_from,
            "linkedin_profile": oancc_application.linkedin_profile,
            "company_id": oancc_application.company_id.id,
        }

        self.assertDictEqual(
            {
                "partner_name": "OneAppNoCompCandidate",
                "partner_phone": "5678",
                "email_from": "oneappnocompcandidate@example.com",
                "linkedin_profile": "linkedin.OneAppNoCompCandidate",
                "company_id": False,
            },
            oancc_app_data,
            "The information from OneAppNoCompCandidate should have transferred from the candidate to the applicant",
        )

        mancc_applications = self.env["hr.applicant"].browse(init["mancc_apps"])

        self.assertCountEqual(
            init["mancc_apps"],
            mancc_applications.ids,
            "The Application for MultiAppNoCompCandidate should still exists",
        )
        mancc_app_data = {
            "partner_name": set(mancc_applications.mapped("partner_name")),
            "partner_phone": set(mancc_applications.mapped("partner_phone")),
            "email_from": set(mancc_applications.mapped("email_from")),
            "linkedin_profile": set(mancc_applications.mapped("linkedin_profile")),
            "company_id": set(mancc_applications.mapped("company_id.id")),
        }
        self.assertDictEqual(
            {
                "partner_name": {"MultiAppNoCompCandidate"},
                "partner_phone": {"6789"},
                "email_from": {"multiappnocompcandidate@example.com"},
                "linkedin_profile": {"linkedin.MultiAppNoCompCandidate"},
                "company_id": set(),
            },
            mancc_app_data,
            "The information from MultiAppNoCompCandidate should have transferred from the candidate to all of the applicants",
        )

        # Other company all cases

        naocc_app = self.env["hr.applicant"].search_count(
            [
                ("partner_name", "=", "NoAppOtherCompCandidate"),
                ("partner_phone", "=", "7890"),
                ("email_from", "=", "noappothercompcandidate@example.com"),
                ("linkedin_profile", "=", "linkedin.NoAppOtherCompCandidate"),
            ]
        )
        self.assertEqual(
            naocc_app,
            1,
            "There should only be 1 application, the talent, for NoAppOtherCompCandidate",
        )

        oaocc_application = self.env["hr.applicant"].browse(init["oaocc_app"])
        self.assertTrue(oaocc_application, "The Application for OneAppOtherCompCandidate should still exists")
        oaocc_app_data = {
            "partner_name": oaocc_application.partner_name,
            "partner_phone": oaocc_application.partner_phone,
            "email_from": oaocc_application.email_from,
            "linkedin_profile": oaocc_application.linkedin_profile,
            "company_id": oaocc_application.company_id.id,
        }

        self.assertDictEqual(
            {
                "partner_name": "OneAppOtherCompCandidate",
                "partner_phone": "8901",
                "email_from": "oneappothercompcandidate@example.com",
                "linkedin_profile": "linkedin.OneAppOtherCompCandidate",
                "company_id": init["other_company_id"],
            },
            oaocc_app_data,
            "The information from OneAppOtherCompCandidate should have transferred from the candidate to the applicant",
        )

        maocc_applications = self.env["hr.applicant"].browse(init["maocc_apps"])

        self.assertCountEqual(
            init["maocc_apps"],
            maocc_applications.ids,
            "The Application for MultiAppCandidate should still exists",
        )
        maocc_app_data = {
            "partner_name": set(maocc_applications.mapped("partner_name")),
            "partner_phone": set(maocc_applications.mapped("partner_phone")),
            "email_from": set(maocc_applications.mapped("email_from")),
            "linkedin_profile": set(maocc_applications.mapped("linkedin_profile")),
            "company_id": set(maocc_applications.mapped("company_id.id")),
        }
        self.assertDictEqual(
            {
                "partner_name": {"MultiAppOtherCompCandidate"},
                "partner_phone": {"9012"},
                "email_from": {"multiappothercompcandidate@example.com"},
                "linkedin_profile": {"linkedin.MultiAppOtherCompCandidate"},
                "company_id": {init["other_company_id"]},
            },
            maocc_app_data,
            "The information from MultiAppCandidate should have transferred from the candidate to all of the applicants",
        )
