from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~18.5")
class TestAppointmentQuestionsM2M(UpgradeCase):
    def _prepare_questions_for_appointment(self, appointment):
        return self.env["appointment.question"].create(
            [
                {
                    "name": "Question Char",
                    "question_type": "char",
                    "appointment_type_id": appointment.id,
                    "sequence": 0,
                },
                {
                    "name": "Question Select",
                    "question_type": "select",
                    "appointment_type_id": appointment.id,
                    "answer_ids": [(0, 0, {"name": f"Select-{i}"}) for i in range(2)],
                    "question_required": True,
                    "sequence": 1,
                },
            ]
        )

    def prepare(self):
        appointment_0, appointment_1 = self.env["appointment.type"].create(
            [{"name": f"Appointment {i}", "appointment_tz": "UTC"} for i in range(2)]
        )

        q_a0_char, q_a0_select = self._prepare_questions_for_appointment(appointment_0)
        q_a1_char, q_a1_select = self._prepare_questions_for_appointment(appointment_1)

        # Create some no-type questions.
        q_a0_no_type_answers = self.env["appointment.question"].create(
            [
                {
                    "name": "Question Without Type",
                    "question_type": False,
                    "appointment_type_id": appointment_0.id,
                    "answer_ids": [(0, 0, {"name": f"To be deleted-{i}"}) for i in range(3)],
                }
            ]
        )
        q_a0_no_type_no_answers = self.env["appointment.question"].create(
            [
                {
                    "name": "Question Without Type And No Answers",
                    "question_type": False,
                    "appointment_type_id": appointment_0.id,
                }
            ]
        )

        appointments_and_questions = [
            (appointment_0.id, [q_a0_char.id, q_a0_select.id, q_a0_no_type_answers.id, q_a0_no_type_no_answers.id]),
            (appointment_1.id, [q_a1_char.id, q_a1_select.id]),
        ]

        return {
            "appointments_and_questions": appointments_and_questions,
            "no_type_questions_and_expected_type": [
                (q_a0_no_type_answers.id, "select"),
                (q_a0_no_type_no_answers.id, "char"),
            ],
        }

    def check(self, init):
        # The phone question is added and unique
        phone_question = self.env["appointment.question"].search([("question_type", "=", "phone")])
        self.assertEqual(len(phone_question), 1)
        self.assertTrue(phone_question.is_default)
        self.assertTrue(phone_question.is_reusable)

        # Assert correct new mapping and that phone question is first in all appointments
        for appointment_id, question_ids in init["appointments_and_questions"]:
            appointment = self.env["appointment.type"].browse(appointment_id).exists()
            self.assertTrue(appointment)
            appointment_questions = appointment.question_ids
            self.assertEqual(appointment_questions[0].question_type, "phone")
            self.assertEqual(appointment_questions[1:].ids, question_ids)
            self.assertTrue(all(appointment_questions.mapped("active")))
            for question in appointment_questions[1:]:
                self.assertEqual(question.appointment_type_ids.ids, appointment.ids)
                self.assertFalse(question.is_default)
                self.assertFalse(question.is_reusable)

        # Ensure no-type questions were correctly typed
        for question_id, expected_type in init["no_type_questions_and_expected_type"]:
            question_record = self.env["appointment.question"].browse(question_id).exists()
            self.assertTrue(question_record)
            self.assertEqual(question_record.question_type, expected_type)
