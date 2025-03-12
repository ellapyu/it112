PRAGMA foreign_keys = ON;

INSERT OR IGNORE INTO category (category_name) VALUES
('Dairy'), ('Meat'), ('Seafood'), ('Plant Protein'), ('Produce'), ('Bakery'),
('Canned Goods'), ('Frozen Food'), ('Pantry');


INSERT OR IGNORE INTO macronutrient (macro_name) VALUES
('Protein'), ('Fat'), ('Carbohydrate'), ('Fiber'), ('Water');


INSERT OR IGNORE INTO ingredient (ingredient_name, category_id) VALUES
('chicken breast', (SELECT id FROM category WHERE category_name = 'Meat')),
('milk', (SELECT id FROM category WHERE category_name = 'Dairy')),
('yogurt', (SELECT id FROM category WHERE category_name = 'Dairy')),
('chicken thigh', (SELECT id FROM category WHERE category_name = 'Meat')),
('salmon', (SELECT id FROM category WHERE category_name = 'Meat')),
('whole wheat bread', (SELECT id FROM category WHERE category_name = 'Bakery')),
('brioche bread', (SELECT id FROM category WHERE category_name = 'Bakery')),
('banana bread', (SELECT id FROM category WHERE category_name = 'Bakery')),
('pinto beans', (SELECT id FROM category WHERE category_name = 'Pantry')),
('chicken stock', (SELECT id FROM category WHERE category_name = 'Pantry')),
('rigatoni', (SELECT id FROM category WHERE category_name = 'Pantry')),
('tofu', (SELECT id FROM category WHERE category_name = 'Plant Protein')),
('butter', (SELECT id FROM category WHERE category_name = 'Dairy')),
('olive oil', (SELECT id FROM category WHERE category_name = 'Pantry')),
('corn', (SELECT id FROM category WHERE category_name = 'Canned Goods')),
('apples', (SELECT id FROM category WHERE category_name = 'Produce')),
('spinach', (SELECT id FROM category WHERE category_name = 'Produce')),
('mushrooms', (SELECT id FROM category WHERE category_name = 'Produce')),
('jiaozi dumplings', (SELECT id FROM category WHERE category_name = 'Frozen Food')),
('beechers flagship mac and cheese', (SELECT id FROM category WHERE category_name = 'Frozen Food')),
('frozen pizza', (SELECT id FROM category WHERE category_name = 'Frozen Food'));


INSERT OR IGNORE INTO ingredient_macronutrient (ingredient_id, macronutrient_id)
VALUES
-- Protein
((SELECT id FROM ingredient WHERE ingredient_name = 'chicken breast'), (SELECT id FROM macronutrient WHERE macro_name = 'Protein')),
((SELECT id FROM ingredient WHERE ingredient_name = 'chicken thigh'), (SELECT id FROM macronutrient WHERE macro_name = 'Protein')),
((SELECT id FROM ingredient WHERE ingredient_name = 'salmon'), (SELECT id FROM macronutrient WHERE macro_name = 'Protein')),
((SELECT id FROM ingredient WHERE ingredient_name = 'milk'), (SELECT id FROM macronutrient WHERE macro_name = 'Protein')),
((SELECT id FROM ingredient WHERE ingredient_name = 'yogurt'), (SELECT id FROM macronutrient WHERE macro_name = 'Protein')),
((SELECT id FROM ingredient WHERE ingredient_name = 'pinto beans'), (SELECT id FROM macronutrient WHERE macro_name = 'Protein')),
((SELECT id FROM ingredient WHERE ingredient_name = 'tofu'), (SELECT id FROM macronutrient WHERE macro_name = 'Protein')),

-- Fat
((SELECT id FROM ingredient WHERE ingredient_name = 'butter'), (SELECT id FROM macronutrient WHERE macro_name = 'Fat')),
((SELECT id FROM ingredient WHERE ingredient_name = 'olive oil'), (SELECT id FROM macronutrient WHERE macro_name = 'Fat')),
((SELECT id FROM ingredient WHERE ingredient_name = 'milk'), (SELECT id FROM macronutrient WHERE macro_name = 'Fat')),
((SELECT id FROM ingredient WHERE ingredient_name = 'yogurt'), (SELECT id FROM macronutrient WHERE macro_name = 'Fat')),
((SELECT id FROM ingredient WHERE ingredient_name = 'salmon'), (SELECT id FROM macronutrient WHERE macro_name = 'Fat')),

-- Carbohydrates
((SELECT id FROM ingredient WHERE ingredient_name = 'whole wheat bread'), (SELECT id FROM macronutrient WHERE macro_name = 'Carbohydrate')),
((SELECT id FROM ingredient WHERE ingredient_name = 'brioche bread'), (SELECT id FROM macronutrient WHERE macro_name = 'Carbohydrate')),
((SELECT id FROM ingredient WHERE ingredient_name = 'banana bread'), (SELECT id FROM macronutrient WHERE macro_name = 'Carbohydrate')),
((SELECT id FROM ingredient WHERE ingredient_name = 'rigatoni'), (SELECT id FROM macronutrient WHERE macro_name = 'Carbohydrate')),
((SELECT id FROM ingredient WHERE ingredient_name = 'corn'), (SELECT id FROM macronutrient WHERE macro_name = 'Carbohydrate')),
((SELECT id FROM ingredient WHERE ingredient_name = 'apples'), (SELECT id FROM macronutrient WHERE macro_name = 'Carbohydrate')),
((SELECT id FROM ingredient WHERE ingredient_name = 'jiaozi dumplings'), (SELECT id FROM macronutrient WHERE macro_name = 'Carbohydrate')),
((SELECT id FROM ingredient WHERE ingredient_name = 'beechers flagship mac and cheese'), (SELECT id FROM macronutrient WHERE macro_name = 'Carbohydrate')),
((SELECT id FROM ingredient WHERE ingredient_name = 'frozen pizza'), (SELECT id FROM macronutrient WHERE macro_name = 'Carbohydrate')),

-- Water
((SELECT id FROM ingredient WHERE ingredient_name = 'milk'), (SELECT id FROM macronutrient WHERE macro_name = 'Water')),
((SELECT id FROM ingredient WHERE ingredient_name = 'yogurt'), (SELECT id FROM macronutrient WHERE macro_name = 'Water')),
((SELECT id FROM ingredient WHERE ingredient_name = 'spinach'), (SELECT id FROM macronutrient WHERE macro_name = 'Water')),
((SELECT id FROM ingredient WHERE ingredient_name = 'mushrooms'), (SELECT id FROM macronutrient WHERE macro_name = 'Water')),

-- Fiber
((SELECT id FROM ingredient WHERE ingredient_name = 'whole wheat bread'), (SELECT id FROM macronutrient WHERE macro_name = 'Fiber')),
((SELECT id FROM ingredient WHERE ingredient_name = 'pinto beans'), (SELECT id FROM macronutrient WHERE macro_name = 'Fiber')),
((SELECT id FROM ingredient WHERE ingredient_name = 'apples'), (SELECT id FROM macronutrient WHERE macro_name = 'Fiber')),
((SELECT id FROM ingredient WHERE ingredient_name = 'spinach'), (SELECT id FROM macronutrient WHERE macro_name = 'Fiber')),
((SELECT id FROM ingredient WHERE ingredient_name = 'mushrooms'), (SELECT id FROM macronutrient WHERE macro_name = 'Fiber'));


INSERT OR IGNORE INTO inventory (user_id, ingredient_id, quantity)
VALUES
((SELECT id FROM user WHERE username = 'ellapyu'), (SELECT id FROM ingredient WHERE ingredient_name = 'chicken breast'), '2 lbs'),
((SELECT id FROM user WHERE username = 'ellapyu'), (SELECT id FROM ingredient WHERE ingredient_name = 'milk'), '1 gallon');
