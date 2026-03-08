-- Run this command in your Supabase SQL Editor to add the want_nominee_id column
-- to the existing picks table, and set up the foreign key constraint.

ALTER TABLE picks
ADD COLUMN want_nominee_id UUID;

-- Now add the foreign key constraint pointing to the nominees table
ALTER TABLE picks
ADD CONSTRAINT fk_picks_want_nominee
FOREIGN KEY (want_nominee_id) REFERENCES nominees(id) ON DELETE CASCADE;
