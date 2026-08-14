"""
End-to-end tests for all 3 sample C-CDA XML documents.
"""

import json
import os
import sys
import unittest

# Ensure src directory is in Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from ccda_parser import parse_ccda_file

SAMPLES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "samples")


class TestSampleDocuments(unittest.TestCase):

    def test_sample_1_continuity_of_care_document(self):
        sample_path = os.path.join(SAMPLES_DIR, "sample_1_continuity_of_care_document.xml")
        self.assertTrue(os.path.exists(sample_path), f"Sample file not found: {sample_path}")

        data = parse_ccda_file(sample_path)

        # 1. Document metadata
        self.assertEqual(data["document_meta"]["title"], "Continuity of Care Document (CCD)")
        self.assertEqual(data["document_meta"]["document_id"]["extension"], "CCD-2023-009182")

        # 2. Patient demographics
        patient = data["patient"]
        self.assertEqual(patient["name"]["first_name"], "Eleanor")
        self.assertEqual(patient["name"]["last_name"], "Vance")
        self.assertEqual(patient["birth_time"], "1975-08-22")
        self.assertEqual(patient["gender"]["code"], "F")
        self.assertEqual(patient["race"]["display_name"], "White")
        self.assertEqual(patient["addresses"][0]["city"], "Springfield")

        # 3. Allergies
        allergies = data["sections"]["allergies"]["entries"]
        self.assertEqual(len(allergies), 2)
        substances = [a["substance"]["display_name"] for a in allergies if a["substance"]]
        self.assertIn("Penicillin G", substances)
        self.assertIn("Peanut", substances)

        # 4. Medications
        medications = data["sections"]["medications"]["entries"]
        self.assertGreaterEqual(len(medications), 3)
        med_names = [m["medication"]["display_name"] for m in medications if m["medication"]]
        self.assertTrue(any("Metformin" in n for n in med_names))
        self.assertTrue(any("Lisinopril" in n for n in med_names))
        self.assertTrue(any("Atorvastatin" in n for n in med_names))

        # 5. Problems
        problems = data["sections"]["problems"]["entries"]
        self.assertGreaterEqual(len(problems), 2)
        prob_names = [p["problem"]["display_name"] for p in problems if p["problem"]]
        self.assertTrue(any("Diabetes" in n for n in prob_names))
        self.assertTrue(any("hypertension" in n.lower() for n in prob_names))

        # 6. Vital signs
        vitals = data["sections"]["vital_signs"]
        self.assertTrue(len(vitals["measurements"]) > 0 or len(vitals["panels"]) > 0)

        # 7. Lab Results
        labs = data["sections"]["results"]
        self.assertTrue(len(labs["results"]) > 0 or len(labs["panels"]) > 0)
        hba1c = [r for r in labs["results"] if "Hemoglobin A1c" in (r.get("test") or {}).get("display_name", "")]
        if hba1c:
            self.assertEqual(hba1c[0]["value"]["value"], 6.8)

        # 8. Immunizations
        imms = data["sections"]["immunizations"]["entries"]
        self.assertGreaterEqual(len(imms), 1)

        # Summary counts
        self.assertGreaterEqual(data["summary"]["counts"]["medications"], 3)
        self.assertGreaterEqual(data["summary"]["counts"]["allergies"], 2)

    def test_sample_2_discharge_summary(self):
        sample_path = os.path.join(SAMPLES_DIR, "sample_2_discharge_summary.xml")
        self.assertTrue(os.path.exists(sample_path), f"Sample file not found: {sample_path}")

        data = parse_ccda_file(sample_path)

        # Patient
        self.assertEqual(data["patient"]["name"]["first_name"], "Marcus")
        self.assertEqual(data["patient"]["name"]["last_name"], "Thorne")
        self.assertEqual(data["patient"]["gender"]["code"], "M")

        # Hospital Course & Chief complaint
        self.assertIn("hospital_course", data["sections"])
        self.assertIn("appendicitis", data["sections"]["hospital_course"]["narrative"].lower())

        # Procedures
        self.assertIn("procedures", data["sections"])
        procs = data["sections"]["procedures"]["entries"]
        self.assertGreaterEqual(len(procs), 1)
        self.assertIn("Appendectomy", procs[0]["procedure"]["display_name"])

        # Discharge meds
        self.assertIn("discharge_medications", data["sections"])
        dm = data["sections"]["discharge_medications"]["entries"]
        self.assertGreaterEqual(len(dm), 1)

    def test_sample_3_cardiology_referral_note(self):
        sample_path = os.path.join(SAMPLES_DIR, "sample_3_cardiology_referral_note.xml")
        self.assertTrue(os.path.exists(sample_path), f"Sample file not found: {sample_path}")

        data = parse_ccda_file(sample_path)

        # Patient
        self.assertEqual(data["patient"]["name"]["first_name"], "Sophia")
        self.assertEqual(data["patient"]["name"]["last_name"], "Rodriguez")

        # Reason for referral
        self.assertIn("reason_for_referral", data["sections"])
        self.assertIn("palpitations", data["sections"]["reason_for_referral"]["narrative"].lower())

        # Vitals
        self.assertIn("vital_signs", data["sections"])
        vitals = data["sections"]["vital_signs"]["measurements"]
        self.assertGreaterEqual(len(vitals), 2)

        # Assessment and plan
        self.assertIn("assessment_and_plan", data["sections"])
        self.assertIn("holter", data["sections"]["assessment_and_plan"]["narrative"].lower())


if __name__ == "__main__":
    unittest.main()
