CREATE TABLE public.patient (
 patient_id TEXT NOT NULL PRIMARY KEY,
 patient_name TEXT NOT NULL,
provider_ids TEXT []
);

CREATE TABLE public.provider (
 provider_id TEXT NOT NULL PRIMARY KEY,
 provider_name TEXT NOT NULL
);

CREATE TABLE public.patient_events (
event_id BIGINT NOT NULL PRIMARY KEY,
patient_id BIGINT NOT NULL,
provider_id BIGINT NOT NULL,
 start_date TIMESTAMPTZ NOT NULL,
 end_date TIMESTAMPTZ,
 event_type TEXT NOT NULL,
 provider_notes TEXT
);