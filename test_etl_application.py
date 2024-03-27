import unittest
from unittest.mock import MagicMock, patch
import etl_application

class TestDataTransfer(unittest.TestCase):

    @patch('etl_application.pyodbc.connect')
    def test_extract_patients(self, mock_connect):
        # Mock cursor and execute method
        mock_cursor = MagicMock()
        mock_cursor.fetchmany.return_value = [(1, 'John'), (2, 'Jane')]
        mock_connect.return_value.cursor.return_value = mock_cursor

        # Call the function under test
        patients = etl_application.extract_patients(mock_cursor)

        # Assertions
        self.assertEqual(len(patients), 2)
        self.assertEqual(patients[0], (1, 'John'))
        self.assertEqual(patients[1], (2, 'Jane'))

    # Similar tests for extract_providers, extract_relationships, and extract_events functions

    def test_transform_data(self):
        # Test data
        patients = [(1, 'John'), (2, 'Jane')]
        providers = [(101, 'Dr. Smith'), (102, 'Dr. Doe')]
        relationships = [(1, 101), (1, 102)]
        events = [(1001, 1, 101, '2023-01-01', '2023-01-02', 'Checkup', 'Notes')]

        # Call the function under test
        transformed_patients, transformed_providers, transformed_relationships, transformed_events = etl_application.transform_data(patients, providers, relationships, events)

        # Assertions
        self.assertEqual(transformed_patients, [('1', 'John'), ('2', 'Jane')])
        self.assertEqual(transformed_providers, [('101', 'Dr. Smith'), ('102', 'Dr. Doe')])
        self.assertEqual(transformed_relationships, [('1', ['101', '102'])])
        self.assertEqual(transformed_events, [(1001, '1', '101', '2023-01-01', '2023-01-02', 'Checkup', 'Notes')])

    @patch('etl_application.psycopg2.connect')
    def test_load_to_postgresql(self, mock_connect):
        # Mock cursor and execute method
        mock_cursor = MagicMock()
        mock_connect.return_value.cursor.return_value = mock_cursor

        # Test data
        data = ([('1', 'John')], [('101', 'Dr. Smith')], [('1', ['101'])], [(1001, '1', '101', '2023-01-01', '2023-01-02', 'Checkup', 'Notes')])

        # Call the function under test
        etl_application.load_to_postgresql(data)

        # Assertions
        mock_cursor.executemany.assert_any_call("INSERT INTO public.patient (patient_id, patient_name) VALUES (%s, %s)", [('1', 'John')])
        mock_cursor.executemany.assert_any_call("INSERT INTO public.providers (provider_id, provider_name) VALUES (%s, %s)", [('101', 'Dr. Smith')])
        mock_cursor.executemany.assert_any_call("INSERT INTO public.patient_provider (patient_id, provider_ids) VALUES (%s, %s)", [('1', ['101'])])
        mock_cursor.executemany.assert_any_call("INSERT INTO public.patient_events (event_id, patient_id, provider_id, start_date, end_date, event_type, provider_notes) VALUES (%s, %s, %s, %s, %s, %s, %s)", [(1001, '1', '101', '2023-01-01', '2023-01-02', 'Checkup', 'Notes')])

if __name__ == "__main__":
    unittest.main()
