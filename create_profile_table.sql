-- Create Profile table
CREATE TABLE IF NOT EXISTS "gerencia_profile" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "role" varchar(20) NOT NULL,
    "phone" varchar(20) NULL,
    "bio" text NULL,
    "date_updated" datetime NOT NULL,
    "user_id" integer NOT NULL UNIQUE REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED
);

-- Create index for user_id
CREATE INDEX IF NOT EXISTS "gerencia_profile_user_id" ON "gerencia_profile" ("user_id");
