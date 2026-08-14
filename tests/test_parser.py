"""
Unit tests for C-CDA XML to JSON parser components.
"""

import json
import os
import sys
import unittest
import xml.etree.ElementTree as ET

# Ensure src directory is in Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from ccda_parser import CCDAParser, parse_ccda
from ccda_parser.utils.code_utils import parse_code, parse_value_element
from ccda_parser.utils.date_utils import format_period, parse_effective_time, parse_hl7_date
from ccda_parser.utils.narrative_utils import extract_narrative_text, parse_narrative_tables
from ccda_parser.utils.xml_utils import parse_xml, strip_namespaces


class TestDateUtils(unittest.TestCase):
    def test_parse_hl7_date(self):
        self.assertEqual(parse_hl7_date("20230514"), "2023-05-14")
        self.assertEqual(parse_hl7_date("20230514153022"), "2023-05-14T15:30:22")
        self.assertEqual(parse_hl7_date("202305141530"), "2023-05-14T15:30:00")
        self.assertEqual(parse_hl7_date("202305"), "2023-05")
        self.assertEqual(parse_hl7_date("2023"), "2023")
        self.assertEqual(parse_hl7_date("20230514153022-0400"), "2023-05-14T15:30:22-04:00")
        self.assertEqual(parse_hl7_date("20230514153022+0000"), "2023-05-14T15:30:22Z")
        self.assertIsNone(parse_hl7_date(None))
        self.assertIsNone(parse_hl7_date(""))

    def test_format_period(self):
        self.assertEqual(format_period("12", "h"), "Twice daily (q12h)")
        self.assertEqual(format_period("24", "h"), "Daily")
        self.assertEqual(format_period("8", "h"), "Three times daily (q8h)")
        self.assertEqual(format_period("6", "h"), "Four times daily (q6h)")
        self.assertEqual(format_period("1", "d"), "Every day")


class TestCodeUtils(unittest.TestCase):
    def test_parse_code_basic(self):
        xml_str = '<code code="44054006" codeSystem="2.16.840.1.113883.6.96" displayName="Type 2 diabetes mellitus"/>'
        el = ET.fromstring(xml_str)
        res = parse_code(el)
        self.assertEqual(res["code"], "44054006")
        self.assertEqual(res["code_system_name"], "SNOMED CT")
        self.assertEqual(res["display_name"], "Type 2 diabetes mellitus")

    def test_parse_value_pq(self):
        xml_str = '<value value="128" unit="mm[Hg]"/>'
        el = ET.fromstring(xml_str)
        res = parse_value_element(el)
        self.assertEqual(res["type"], "PQ")
        self.assertEqual(res["value"], 128.0)
        self.assertEqual(res["unit"], "mm[Hg]")


class TestNarrativeUtils(unittest.TestCase):
    def test_extract_narrative_text(self):
        xml_str = """
        <text>
            <paragraph>Patient presented with chest pain.</paragraph>
            <list>
                <item>Item 1</item>
                <item>Item 2</item>
            </list>
        </text>
        """
        el = ET.fromstring(xml_str)
        text = extract_narrative_text(el)
        self.assertIn("Patient presented with chest pain.", text)
        self.assertIn("• Item 1", text)
        self.assertIn("• Item 2", text)

    def test_parse_narrative_tables(self):
        xml_str = """
        <text>
            <table>
                <thead><tr><th>Med</th><th>Dose</th></tr></thead>
                <tbody><tr><td>Aspirin</td><td>81mg</td></tr></tbody>
            </table>
        </text>
        """
        el = ET.fromstring(xml_str)
        tables = parse_narrative_tables(el)
        self.assertEqual(len(tables), 1)
        self.assertEqual(tables[0]["headers"], ["Med", "Dose"])
        self.assertEqual(tables[0]["rows"][0], {"Med": "Aspirin", "Dose": "81mg"})


class TestMinimalCCDA(unittest.TestCase):
    def test_minimal_document(self):
        xml_str = """<?xml version="1.0"?>
        <ClinicalDocument xmlns="urn:hl7-org:v3">
            <title>Test CCDA Document</title>
            <effectiveTime value="20230514"/>
            <recordTarget>
                <patientRole>
                    <patient>
                        <name><given>John</given><family>Doe</family></name>
                        <administrativeGenderCode code="M" displayName="Male"/>
                        <birthTime value="19800101"/>
                    </patient>
                </patientRole>
            </recordTarget>
            <component>
                <structuredBody>
                    <component>
                        <section>
                            <code code="48765-2" displayName="Allergies"/>
                            <title>Allergies</title>
                            <text><paragraph>No Known Drug Allergies (NKDA)</paragraph></text>
                        </section>
                    </component>
                </structuredBody>
            </component>
        </ClinicalDocument>
        """
        data = parse_ccda(xml_str)
        self.assertEqual(data["document_meta"]["title"], "Test CCDA Document")
        self.assertEqual(data["patient"]["name"]["full_name"], "John Doe")
        self.assertEqual(data["patient"]["birth_time"], "1980-01-01")
        self.assertEqual(data["patient"]["gender"]["code"], "M")
        self.assertIn("allergies", data["sections"])
        self.assertIn("No Known Drug Allergies", data["sections"]["allergies"]["narrative"])


if __name__ == "__main__":
    unittest.main()
