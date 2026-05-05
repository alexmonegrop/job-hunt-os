-- =============================================================================
-- 02-jobhunt-schema.sql
-- 7-table schema for the job-hunt-os data backend.
-- Runs once at first postgres boot, against the `jobhunt` database (default).
--
-- After this runs, NocoDB can connect to the `jobhunt` database as a
-- Data Source and surface these tables. tools/setup/init-nocodb.py
-- discovers the resulting base id + link-field ids.
--
-- Schema design notes:
--   - Single `users` table for multi-user support (1 row = 1 person being
--     job-hunted for). All data tables have a `user_id` FK to filter by user.
--   - No CHECK constraints on user-customisable enums (industry, job_board,
--     expansion_status) — those values come from config/*.yaml at the
--     application level. CHECKs remain on truly-fixed lifecycle enums
--     (status, application_status, contact_priority).
--   - Foreign keys are simple integer FKs. NocoDB surfaces them as
--     LinkToAnotherRecord fields and discovers their numeric IDs at runtime
--     (see tools/setup/init-nocodb.py).
--   - All tables have `created_at` and `updated_at` timestamps with
--     auto-update triggers.
-- =============================================================================

-------------------------------------------------------
-- 0. users (multi-user support)
-------------------------------------------------------
CREATE TABLE users (
    id              SERIAL PRIMARY KEY,
    slug            TEXT NOT NULL UNIQUE,
    full_name       TEXT NOT NULL,
    email           TEXT,
    phone           TEXT,
    linkedin        TEXT,
    location        TEXT,
    target_roles    TEXT,
    notes           TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Seed a default user so single-user setups work out of the box.
-- Multi-user setups will add additional rows via /onboard-user.
INSERT INTO users (slug, full_name, notes)
VALUES ('default', 'Default User', 'Default user seeded by 02-jobhunt-schema.sql; rename via /onboard-user.');

-------------------------------------------------------
-- 1. target_companies (hub table)
-------------------------------------------------------
CREATE TABLE target_companies (
    id                  SERIAL PRIMARY KEY,
    user_id             INTEGER NOT NULL DEFAULT 1 REFERENCES users(id),
    company_name        TEXT NOT NULL,
    industry            TEXT,
    hq_location         TEXT,
    employee_count      INTEGER,
    website             TEXT,
    tier                TEXT CHECK (tier IN (
                            'Tier 1 - Highest Priority',
                            'Tier 2 - High Priority',
                            'Tier 3 - Medium Priority'
                        )),
    expansion_status    TEXT,
    why_strong_fit      TEXT,
    recent_signals      TEXT,
    research_date       DATE,
    workstream          TEXT[] DEFAULT '{}',
    notes               TEXT,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

-------------------------------------------------------
-- 2. target_contacts (FK to target_companies)
-------------------------------------------------------
CREATE TABLE target_contacts (
    id                  SERIAL PRIMARY KEY,
    user_id             INTEGER NOT NULL DEFAULT 1 REFERENCES users(id),
    full_name           TEXT NOT NULL,
    title_role          TEXT,
    linkedin_profile    TEXT,
    company_id          INTEGER REFERENCES target_companies(id),
    why_right_person    TEXT,
    contact_source      TEXT DEFAULT 'LinkedIn',
    contact_priority    TEXT CHECK (contact_priority IN (
                            'Primary',
                            'Secondary',
                            'Backup'
                        )),
    email               TEXT,
    phone               TEXT,
    location            TEXT,
    added_date          DATE,
    notes               TEXT,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

-------------------------------------------------------
-- 3. sales_pipeline (FKs to contacts + companies)
-------------------------------------------------------
CREATE TABLE sales_pipeline (
    id                  SERIAL PRIMARY KEY,
    user_id             INTEGER NOT NULL DEFAULT 1 REFERENCES users(id),
    pipeline_name       TEXT NOT NULL,
    contact_id          INTEGER REFERENCES target_contacts(id),
    company_id          INTEGER REFERENCES target_companies(id),
    pipeline_stage      TEXT DEFAULT '1. Research',
    temperature         TEXT DEFAULT 'Cold',
    outreach_date       DATE,
    last_activity       DATE,
    next_step           TEXT,
    notes               TEXT,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

-------------------------------------------------------
-- 4. interactions (FKs to pipeline + contacts)
-------------------------------------------------------
CREATE TABLE interactions (
    id                  SERIAL PRIMARY KEY,
    user_id             INTEGER NOT NULL DEFAULT 1 REFERENCES users(id),
    interaction_type    TEXT CHECK (interaction_type IN (
                            'Message Drafted',
                            'Message Sent',
                            'Reply Received',
                            'Meeting Scheduled',
                            'Meeting Completed',
                            'Follow-Up Sent',
                            'Application Submitted',
                            'Application Follow-Up',
                            'Resume Tailored',
                            'Job Posting Saved'
                        )),
    interaction_date    TIMESTAMPTZ,
    target_contact_id   INTEGER REFERENCES target_contacts(id),
    pipeline_entry_id   INTEGER REFERENCES sales_pipeline(id),
    interaction_summary TEXT,
    subject_topic       TEXT,
    details             TEXT,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

-------------------------------------------------------
-- 5. job_postings (FK to target_companies)
-------------------------------------------------------
CREATE TABLE job_postings (
    id                  SERIAL PRIMARY KEY,
    user_id             INTEGER NOT NULL DEFAULT 1 REFERENCES users(id),
    company_name        TEXT NOT NULL,
    job_title           TEXT NOT NULL,
    company_id          INTEGER REFERENCES target_companies(id),
    job_board           TEXT,
    job_url             TEXT,
    location            TEXT,
    remote_status       TEXT CHECK (remote_status IN (
                            'On-site',
                            'Hybrid',
                            'Remote'
                        )),
    posted_date         DATE,
    discovered_date     DATE,
    job_description     TEXT,
    key_requirements    TEXT,
    role_category       TEXT,
    fit_score           INTEGER CHECK (fit_score BETWEEN 1 AND 10),
    fit_analysis        TEXT,
    status              TEXT DEFAULT 'New' CHECK (status IN (
                            'New',
                            'Reviewing',
                            'Applying',
                            'Applied',
                            'Interview',
                            'Rejected',
                            'Withdrawn',
                            'Expired'
                        )),
    resume_version_used TEXT,
    notes               TEXT,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

-------------------------------------------------------
-- 6. applications (FKs to postings, companies, contacts, pipeline)
-------------------------------------------------------
CREATE TABLE applications (
    id                      SERIAL PRIMARY KEY,
    user_id                 INTEGER NOT NULL DEFAULT 1 REFERENCES users(id),
    application_name        TEXT NOT NULL,
    job_posting_id          INTEGER REFERENCES job_postings(id),
    company_id              INTEGER REFERENCES target_companies(id),
    application_date        DATE,
    application_method      TEXT CHECK (application_method IN (
                                'Direct',
                                'Easy Apply',
                                'Company Portal',
                                'Recruiter',
                                'Referral'
                            )),
    resume_version          TEXT,
    cover_letter            BOOLEAN DEFAULT FALSE,
    application_status      TEXT DEFAULT 'Preparing' CHECK (application_status IN (
                                'Preparing',
                                'Submitted',
                                'Acknowledged',
                                'Screening',
                                'Interview Scheduled',
                                'Interview Completed',
                                'Offer',
                                'Rejected',
                                'Withdrawn'
                            )),
    response_date           DATE,
    networking_contact_id   INTEGER REFERENCES target_contacts(id),
    pipeline_entry_id       INTEGER REFERENCES sales_pipeline(id),
    follow_up_date          DATE,
    notes                   TEXT,
    created_at              TIMESTAMPTZ DEFAULT NOW(),
    updated_at              TIMESTAMPTZ DEFAULT NOW()
);

-------------------------------------------------------
-- Indexes for common queries
-------------------------------------------------------
CREATE INDEX idx_companies_user        ON target_companies(user_id);
CREATE INDEX idx_contacts_user         ON target_contacts(user_id);
CREATE INDEX idx_contacts_company      ON target_contacts(company_id);
CREATE INDEX idx_pipeline_user         ON sales_pipeline(user_id);
CREATE INDEX idx_pipeline_contact      ON sales_pipeline(contact_id);
CREATE INDEX idx_pipeline_company      ON sales_pipeline(company_id);
CREATE INDEX idx_interactions_user     ON interactions(user_id);
CREATE INDEX idx_interactions_contact  ON interactions(target_contact_id);
CREATE INDEX idx_interactions_pipeline ON interactions(pipeline_entry_id);
CREATE INDEX idx_postings_user         ON job_postings(user_id);
CREATE INDEX idx_postings_company      ON job_postings(company_id);
CREATE INDEX idx_postings_status       ON job_postings(status);
CREATE INDEX idx_applications_user     ON applications(user_id);
CREATE INDEX idx_applications_posting  ON applications(job_posting_id);
CREATE INDEX idx_applications_company  ON applications(company_id);
CREATE INDEX idx_applications_status   ON applications(application_status);

-------------------------------------------------------
-- Updated_at trigger function
-------------------------------------------------------
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_users_updated            BEFORE UPDATE ON users            FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_target_companies_updated BEFORE UPDATE ON target_companies FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_target_contacts_updated  BEFORE UPDATE ON target_contacts  FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_sales_pipeline_updated   BEFORE UPDATE ON sales_pipeline   FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_interactions_updated     BEFORE UPDATE ON interactions     FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_job_postings_updated     BEFORE UPDATE ON job_postings     FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_applications_updated     BEFORE UPDATE ON applications     FOR EACH ROW EXECUTE FUNCTION update_updated_at();
