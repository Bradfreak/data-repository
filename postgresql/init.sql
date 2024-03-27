CREATE DATABASE EHR_Healthcare_Data;

USE EHR_Healthcare_Data;

-- Create table for Patients
CREATE TABLE dbo.patient (
    patient_id BIGINT PRIMARY KEY,
    patient_name VARCHAR(500) NOT NULL
);

-- Create table for Providers
CREATE TABLE dbo.providers (
    provider_id BIGINT PRIMARY KEY,
    provider_name VARCHAR(500) NOT NULL,
    provider_type VARCHAR(500)
);

-- Create table for Patient-Provider Relationships
CREATE TABLE dbo.patient_provider_relationship (
    patient_id BIGINT,
    provider_id BIGINT,
    FOREIGN KEY (patient_id) REFERENCES dbo.patient(patient_id),
    FOREIGN KEY (provider_id) REFERENCES dbo.providers(provider_id)
);

-- Create table for Patient Events
CREATE TABLE dbo.patient_events (
    event_id BIGINT PRIMARY KEY,
    patient_id BIGINT,
    provider_id BIGINT,
    start_date DATETIME,
    end_date DATETIME,
    event_type VARCHAR(100),
    provider_notes VARCHAR(100),
    FOREIGN KEY (patient_id) REFERENCES dbo.patient(patient_id),
    FOREIGN KEY (provider_id) REFERENCES dbo.providers(provider_id)
);
