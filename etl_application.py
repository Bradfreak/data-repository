import pyodbc
import psycopg2
import multiprocessing
import logging

# Configure logging
logging.basicConfig(filename='etl.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# SQL Server connection parameters
SQL_SERVER_CONNECTION_STRING = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=172.19.0.3;DATABASE=EHR_Healthcare_Data;UID=sa;PWD=admin_001@EHR'

# PostgreSQL connection parameters
POSTGRESQL_CONNECTION_STRING = "dbname='Holmusk_Data_Lake' user='admin' host='172.19.0.2' password='admin_001@Holmusk' port='5432'"

def extract_patients(cursor, batch_size=1000):
    patients = []
    try:
        cursor.execute("SELECT patient_id, patient_name FROM dbo.patient")
        while True:
            batch = cursor.fetchmany(batch_size)
            if not batch:
                break
            patients.extend(batch)
    except Exception as e:
        logging.error("Error occurred during extraction of patients: %s", str(e))
    return patients

def extract_providers(cursor, batch_size=1000):
    providers = []
    try:
        cursor.execute("SELECT provider_id, provider_name FROM dbo.providers")
        while True:
            batch = cursor.fetchmany(batch_size)
            if not batch:
                break
            providers.extend(batch)
    except Exception as e:
        logging.error("Error occurred during extraction of providers: %s", str(e))
    return providers

def extract_relationships(cursor, batch_size=1000):
    relationships = []
    try:
        cursor.execute("SELECT patient_id, provider_id FROM dbo.patient_provider_relationship")
        while True:
            batch = cursor.fetchmany(batch_size)
            if not batch:
                break
            relationships.extend(batch)
    except Exception as e:
        logging.error("Error occurred during extraction of relationships: %s", str(e))
    return relationships

def extract_events(cursor, batch_size=1000):
    events = []
    try:
        cursor.execute("SELECT event_id, patient_id, provider_id, start_date, end_date, event_type, provider_notes FROM dbo.patient_events")
        while True:
            batch = cursor.fetchmany(batch_size)
            if not batch:
                break
            events.extend(batch)
    except Exception as e:
        logging.error("Error occurred during extraction of events: %s", str(e))
    return events

def transform_data(patients, providers, relationships, events):
    # Transform data as per PostgreSQL schema
    transformed_patients = [(str(patient[0]), patient[1]) for patient in patients]
    transformed_providers = [(str(provider[0]), provider[1]) for provider in providers]
    transformed_events = [(event[0], str(event[1]), str(event[2]), event[3], event[4], event[5], event[6]) for event in events]

    # Group provider ids by patient id
    patient_provider_map = {}
    for relation in relationships:
        patient_id, provider_id = str(relation[0]), str(relation[1])
        if patient_id not in patient_provider_map:
            patient_provider_map[patient_id] = [provider_id]
        else:
            patient_provider_map[patient_id].append(provider_id)

    transformed_relationships = [(patient_id, provider_ids) for patient_id, provider_ids in patient_provider_map.items()]

    return transformed_patients, transformed_providers, transformed_relationships, transformed_events

def load_to_postgresql(data, batch_size=1000):
    patients, providers, relationships, events = data
    try:
        conn = psycopg2.connect(POSTGRESQL_CONNECTION_STRING)
        cursor = conn.cursor()

        # Load patients in batches
        for i in range(0, len(patients), batch_size):
            batch = patients[i:i+batch_size]
            cursor.executemany("INSERT INTO public.patient (patient_id, patient_name) VALUES (%s, %s)", batch)

        # Load providers in batches
        for i in range(0, len(providers), batch_size):
            batch = providers[i:i+batch_size]
            cursor.executemany("INSERT INTO public.providers (provider_id, provider_name) VALUES (%s, %s)", batch)

        # Load patient-provider relationships in batches
        for i in range(0, len(relationships), batch_size):
            batch = relationships[i:i+batch_size]
            cursor.executemany("INSERT INTO public.patient_provider (patient_id, provider_ids) VALUES (%s, %s)", batch)

        # Load patient events in batches
        for i in range(0, len(events), batch_size):
            batch = events[i:i+batch_size]
            cursor.executemany("INSERT INTO public.patient_events (event_id, patient_id, provider_id, start_date, end_date, event_type, provider_notes) VALUES (%s, %s, %s, %s, %s, %s, %s)", batch)

        conn.commit()
        logging.info("Data loaded successfully to PostgreSQL.")
    except Exception as e:
        logging.error("Error occurred during loading to PostgreSQL: %s", str(e))
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def parallel_transform(data_chunks):
    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        transformed_data = pool.starmap(transform_data, data_chunks)
    return transformed_data

def run_data_extraction():
    patients, providers, relationships, events = None, None, None, None
    try:
        conn = pyodbc.connect(SQL_SERVER_CONNECTION_STRING)
        cursor = conn.cursor()

        # Extract patients
        patients = extract_patients(cursor)
        # Extract providers
        providers = extract_providers(cursor)
        # Extract patient-provider relationships
        relationships = extract_relationships(cursor)
        # Extract patient events
        events = extract_events(cursor)

    except Exception as e:
        logging.error("An error occurred during data extraction: %s", str(e))
    finally:
        cursor.close()
        conn.close()
        return patients, providers, relationships, events

def run_data_transformation(patients, providers, relationships, events):
    transformed_data = None
    try:
        data_chunks = [(patients, providers, relationships, events)]
        transformed_data = parallel_transform(data_chunks)
    except Exception as e:
        logging.error("An error occurred during data transformation: %s", str(e))
    return transformed_data

if __name__ == "__main__":
    try:
        patients, providers, relationships, events = run_data_extraction()
        if patients and providers and relationships and events:
            transformed_data = run_data_transformation(patients, providers, relationships, events)
            for data in transformed_data:
                load_to_postgresql(data)
    except Exception as e:
        logging.error("An unexpected error occurred: %s", str(e))
