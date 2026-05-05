-- =============================================================================
-- 01-create-databases.sql
-- Runs once at first postgres boot.
-- The `jobhunt` database (the schema target) is created by POSTGRES_DB env.
-- This file creates the `nocodb` metadata database for NocoDB itself.
-- =============================================================================

CREATE DATABASE nocodb;

GRANT ALL PRIVILEGES ON DATABASE nocodb TO jobhunt;
