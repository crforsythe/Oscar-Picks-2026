-- Optional script to reset data nicely
-- TRUNCATE categories CASCADE;

-- Insert some dummy categories
INSERT INTO categories (name, point_value) VALUES
('Best Picture', 10),
('Best Actor', 5),
('Best Actress', 5),
('Best Director', 5)
ON CONFLICT DO NOTHING; -- in case we run it multiple times

-- Insert some dummy nominees. 
-- In a real scenario we'd query the category ID first, but for a simple seed script, 
-- we can use a subquery or do it manually if we knew the UUIDs.
-- Here is a script that uses subqueries to find the right category ID:

WITH cat AS (SELECT id, name FROM categories)
INSERT INTO nominees (category_id, name, movie) VALUES
-- Best Picture
((SELECT id FROM cat WHERE name = 'Best Picture'), 'Dune: Part Two', 'Dune: Part Two'),
((SELECT id FROM cat WHERE name = 'Best Picture'), 'Oppenheimer 2: The Return', 'Oppenheimer 2: The Return'),
((SELECT id FROM cat WHERE name = 'Best Picture'), 'Barbie 2', 'Barbie 2'),

-- Best Actor
((SELECT id FROM cat WHERE name = 'Best Actor'), 'Timothée Chalamet', 'Dune: Part Two'),
((SELECT id FROM cat WHERE name = 'Best Actor'), 'Cillian Murphy', 'Oppenheimer 2: The Return'),

-- Best Actress
((SELECT id FROM cat WHERE name = 'Best Actress'), 'Margot Robbie', 'Barbie 2'),
((SELECT id FROM cat WHERE name = 'Best Actress'), 'Zendaya', 'Dune: Part Two'),

-- Best Director
((SELECT id FROM cat WHERE name = 'Best Director'), 'Denis Villeneuve', 'Dune: Part Two'),
((SELECT id FROM cat WHERE name = 'Best Director'), 'Greta Gerwig', 'Barbie 2'),
((SELECT id FROM cat WHERE name = 'Best Director'), 'Christopher Nolan', 'Oppenheimer 2: The Return');
