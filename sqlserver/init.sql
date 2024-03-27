USE EHR_Healthcare_Data;

CREATE TABLE dbo.patient (
patient_id BIGINT,
patient_name VARCHAR (500)
);

CREATE TABLE dbo.providers (
 provider_id BIGINT,
provider_name VARCHAR (500),
provider_type VARCHAR (500)
);

CREATE TABLE dbo.patient_provider_relationship (
patient_id BIGINT,
provider_id BIGINT
);

CREATE TABLE dbo.patient_events (
 event_id BIGINT,
 patient_id BIGINT,
provider_id BIGINT,
 start_date DATETIME,
 end_date DATETIME,
 event_type VARCHAR (100),
 provider_notes VARCHAR (100)
);