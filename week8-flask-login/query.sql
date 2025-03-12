-- display all ingredients and categories
SELECT ingredient_name AS ingredient, category.category_name AS category
FROM ingredient
JOIN category ON ingredient.category_id = category.id
ORDER BY category;

--display ingredients and their macros
SELECT ingredient.ingredient_name, macronutrient.macro_name
FROM ingredient_macronutrient
JOIN ingredient ON ingredient_macronutrient.ingredient_id = ingredient.id
JOIN macronutrient ON ingredient_macronutrient.macronutrient_id = macronutrient.id
ORDER BY ingredient.ingredient_name;