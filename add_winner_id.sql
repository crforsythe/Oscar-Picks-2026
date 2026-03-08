-- Run this command in your Supabase SQL Editor to add the winner_id column
-- to the existing categories table, and then set up the foreign key constraint.

ALTER TABLE categories
ADD COLUMN winner_id UUID;

-- Now add the foreign key constraint pointing to the nominees table
ALTER TABLE categories
ADD CONSTRAINT fk_categories_winner
FOREIGN KEY (winner_id) REFERENCES nominees(id) ON DELETE SET NULL;
