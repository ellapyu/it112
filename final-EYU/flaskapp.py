from flask import Flask, request, render_template, redirect, url_for, session, g
from flask_bcrypt import Bcrypt
from flask_wtf import CSRFProtect
from forms import ItemForm, UpdateForm, CreateUserForm, LoginForm, InventoryForm, InventoryItemForm
from dotenv import load_dotenv
import os
import sqlite3
import requests

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')
print("SECRET KEY LOADED:", app.secret_key)

csrf = CSRFProtect(app)
bcrypt = Bcrypt(app)

SPOONACULAR_API_KEY = os.getenv("SPOONACULAR_API_KEY")

DATABASE = 'inventory.db'

# connect database
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row 
    return db

#close connection
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        if form.user:
            session['user_id'] = form.user["id"]
            session['username'] = form.user["username"]
            return redirect(url_for('index'))

    return render_template('login.html', form=form) 

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = CreateUserForm()

    if form.validate_on_submit():
        username = form.username.data
        email= form.email.data
        password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        db = get_db()
        cur = db.cursor()

        cur.execute("INSERT INTO user (username, email, hashed_password) VALUES (?,?,?)", (username, email, password))
        db.commit()

        return redirect(url_for('login'))
    return render_template('register.html', form=form)

##########################################################################################################
## home page is logged in user's ingredient inventory
@app.route('/', methods=['GET'])
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    db = get_db()
    cur = db.cursor()

    cur.execute("SELECT ingredient_name FROM ingredient ORDER BY ingredient_name;")
    all_ingredients = [row["ingredient_name"] for row in cur.fetchall()]

    inventory_form = InventoryForm()

    cur.execute("SELECT id FROM user WHERE username = ?", (session['username'],))
    user = cur.fetchone()
    user_id = user["id"]

    cur.execute("""
        SELECT inventory.id, 
                ingredient.ingredient_name AS ingredient,
                category.category_name AS category,
                inventory.quantity,
                inventory.last_updated,
                GROUP_CONCAT(macronutrient.macro_name, ', ') AS macros
        FROM inventory
        JOIN category ON inventory.category_id = category.id
        JOIN ingredient ON inventory.ingredient_id = ingredient.id
        LEFT JOIN ingredient_macronutrient ON ingredient.id = ingredient_macronutrient.ingredient_id
        LEFT JOIN macronutrient ON ingredient_macronutrient.macronutrient_id = macronutrient.id
        WHERE inventory.user_id = ?
        GROUP BY inventory.id, ingredient.ingredient_name, category.category_name, inventory.quantity, inventory.last_updated
        ORDER BY inventory.last_updated DESC;
    """, (user_id,))
    user_inventory = cur.fetchall()

    return render_template('index.html', user_inventory = user_inventory, inventory_form=inventory_form, all_ingredients=all_ingredients, selected_inventory_id=None, update_form=UpdateForm())

# ADD AN EXISTING INGREDIENT TO INVENTORY
@app.route('/add_ingredient', methods=['POST'])
def add_ingredient():
    if 'username' not in session:
        return redirect(url_for('login'))

    db = get_db()
    cur = db.cursor()

    cur.execute("SELECT id FROM user WHERE username = ?", (session['username'],))
    user = cur.fetchone()
    user_id = user["id"]

    inventory_form = InventoryForm()

    ## if form validation fails, fetch user inventory data to repopulate table on add_ingredient
    if not inventory_form.validate_on_submit():
        cur.execute("""
            SELECT inventory.id, 
                    ingredient.ingredient_name AS ingredient,
                    category.category_name AS category,
                    inventory.quantity,
                    inventory.last_updated,
                    GROUP_CONCAT(macronutrient.macro_name, ', ') AS macros
            FROM inventory
            JOIN category ON inventory.category_id = category.id
            JOIN ingredient ON inventory.ingredient_id = ingredient.id
            LEFT JOIN ingredient_macronutrient ON ingredient.id = ingredient_macronutrient.ingredient_id
            LEFT JOIN macronutrient ON ingredient_macronutrient.macronutrient_id = macronutrient.id
            WHERE inventory.user_id = ?
            GROUP BY inventory.id, ingredient.ingredient_name, category.category_name, inventory.quantity, inventory.last_updated
            ORDER BY inventory.last_updated DESC;
        """, (user_id,))
        user_inventory = cur.fetchall()

        return render_template('index.html', inventory_form=inventory_form, user_inventory=user_inventory, update_form=UpdateForm())
    
    # get input from form -- desired ingredient into inventory
    ingredient_name = inventory_form.ingredient.data.strip().lower()
    quantity = inventory_form.quantity.data.strip().lower()

    # ingredient must exist in ingredient table already, so check if it does
    cur.execute("SELECT id, category_id FROM ingredient WHERE ingredient_name = ?", (ingredient_name,))
    ingredient = cur.fetchone()

    # if it doesn't exist, send form responses to add_inventory_item route to add to ingredient table
    if not ingredient:
        return redirect(url_for('add_inventory_item', ingredient_name=ingredient_name, quantity=quantity))

    # get id's of the existing ingredient for future reference
    ingredient_id = ingredient["id"]
    category_id = ingredient["category_id"]

    # check if ingredient is already in user inventory
    cur.execute("SELECT id FROM inventory WHERE user_id = ? AND ingredient_id = ?", (user_id, ingredient_id))
    existing_inventory = cur.fetchone()

    # if it is, give error and fetch user invetory data to repopulate table on add_ingredient
    if existing_inventory:
        inventory_form.ingredient.errors.append(f"'{ingredient_name}' is already in your inventory. Edit to update information.")

        cur.execute("""
            SELECT inventory.id, 
                    ingredient.ingredient_name AS ingredient,
                    category.category_name AS category,
                    inventory.quantity,
                    inventory.last_updated,
                    GROUP_CONCAT(macronutrient.macro_name, ', ') AS macros
            FROM inventory
            JOIN category ON inventory.category_id = category.id
            JOIN ingredient ON inventory.ingredient_id = ingredient.id
            LEFT JOIN ingredient_macronutrient ON ingredient.id = ingredient_macronutrient.ingredient_id
            LEFT JOIN macronutrient ON ingredient_macronutrient.macronutrient_id = macronutrient.id
            WHERE inventory.user_id = ?
            GROUP BY inventory.id, ingredient.ingredient_name, category.category_name, inventory.quantity, inventory.last_updated
            ORDER BY inventory.last_updated DESC;
        """, (user_id,))
        user_inventory = cur.fetchall()

        return render_template('index.html', inventory_form=inventory_form, user_inventory=user_inventory, update_form=UpdateForm())

    # After validation successful, insert existing ingredient to user inventory
    cur.execute("""
        INSERT INTO inventory (user_id, ingredient_id, category_id, quantity)
        VALUES (?, ?, ?, ?)
    """, (user_id, ingredient_id, category_id, quantity))
    db.commit()

    # success, go back to inventory page
    return redirect(url_for('index'))

### ingredient table page. users can see all ingredients in database across users
@app.route('/ingredient')
def ingredientpage():
    if 'username' not in session:
        return redirect(url_for('login'))

    db = get_db()
    cur = db.cursor()

    # fetch all ingredient info, sorted by category
    cur.execute("""
        SELECT ingredient.id, category.category_name AS category, ingredient.ingredient_name AS ingredient
        FROM ingredient
        JOIN category ON ingredient.category_id = category.id
        ORDER BY category.category_name;
    """)
    ingredientInventory = cur.fetchall()

    # fetch categories for dropdown
    cur.execute("""
                SELECT category_name
                FROM category
                ORDER BY category_name;
            """)
    categories = [("", "Select a Category")] + [(row["category_name"], row["category_name"]) for row in cur.fetchall()]

    # fetch macros for checkboxes
    cur.execute("SELECT id, macro_name FROM macronutrient ORDER BY macro_name;")
    macros = [(row["id"], row["macro_name"]) for row in cur.fetchall()]

    # initialize form and populate selection choices
    item_form = ItemForm()
    item_form.category.choices = categories
    item_form.macros.choices = macros 

    # render ingredient page with fetched data
    return render_template('ingredient.html', ingredientInventory = ingredientInventory, item_form = item_form)

## handles adding item to ingredients when redirected from inventory page
@app.route('/add_inventory_item', methods=['POST', 'GET'])
def add_inventory_item():
    if 'username' not in session:
        return redirect(url_for('login'))

    ## fetch ingredient name and quantity when redirected
    ingredient_name = request.args.get('ingredient_name', '').strip().lower()
    quantity = request.args.get('quantity', '').strip().lower()
    
    db = get_db()
    cur = db.cursor()

    # get user from session
    cur.execute("SELECT id FROM user WHERE username = ?", (session['username'],))
    user = cur.fetchone()
    user_id = user["id"]

    # initialize form for inventory
    item_form = InventoryItemForm()

    # prefill form on redirect to this page
    if request.method == "GET":
        item_form.item.data = ingredient_name  
        item_form.quantity.data = quantity

    # get categories for dropdown
    cur.execute("""
        SELECT category_name
        FROM category
        ORDER BY category_name;
    """)
    categories = [("", "Select a Category")] + [(row["category_name"], row["category_name"]) for row in cur.fetchall()]
    item_form.category.choices = categories

    # get macros for checkboxes
    cur.execute("SELECT id, macro_name FROM macronutrient ORDER BY macro_name;")
    macros = [(row["id"], row["macro_name"]) for row in cur.fetchall()]
    item_form.macros.choices = macros

    # fetch all ingredient info, sorted by category for display
    cur.execute("""
        SELECT ingredient.id, ingredient.ingredient_name AS ingredient, category.category_name AS category
        FROM ingredient
        JOIN category ON ingredient.category_id = category.id
        ORDER BY category.category_name;
    """)
    ingredientInventory = cur.fetchall()

    # handle form submission
    if request.method == "POST" and item_form.validate_on_submit():
        item_name = item_form.item.data.strip()
        category_name = item_form.category.data  
        quantity = item_form.quantity.data.strip()
        selected_macros = item_form.macros.data


        # validate category
        cur.execute("SELECT id FROM category WHERE category_name = ?", (category_name,))
        category = cur.fetchone()
        
        if category is None:
            item_form.category.errors.append("You must choose a valid category.") 
            return render_template('add_inventory_item.html', ingredientInventory=ingredientInventory, item_form=item_form)

        category_id = category[0] 

        # check if ingredient exists in ingredient table
        cur.execute("SELECT id FROM ingredient WHERE ingredient_name = ? AND category_id = ?", (item_name, category_id))
        existing_ingredient = cur.fetchone()

        # prevent duplicates
        if existing_ingredient:
            item_form.item.errors.append(f"'{item_name}' already exists in the database.") 
            return render_template('add_inventory_item.html', ingredientInventory=ingredientInventory, item_form=item_form)
        
        # add ingredient to table w/ macros
        else:
            cur.execute('INSERT INTO ingredient (ingredient_name, category_id) VALUES (?,?)', (item_name, category_id))
            ingredient_id = cur.lastrowid  
            db.commit()

            for macro_id in selected_macros:
                cur.execute("INSERT INTO ingredient_macronutrient (ingredient_id, macronutrient_id) VALUES (?, ?)", (ingredient_id, macro_id))
                db.commit()

        # check if ingredient is in user inventory
        cur.execute("SELECT id FROM inventory WHERE user_id = ? AND ingredient_id = ?", (user_id, ingredient_id))
        existing_inventory = cur.fetchone()

        if not existing_inventory:
            # add to inventory
            cur.execute("""
                INSERT INTO inventory (user_id, ingredient_id, category_id, quantity)
                VALUES (?, ?, ?, ?)
            """, (user_id, ingredient_id, category_id, quantity))
            db.commit()

        #redirect to inventory page after submission
        return redirect(url_for('index'))
    
    # render this page with prefilled form data
    return render_template('add_inventory_item.html', ingredientInventory=ingredientInventory, item_form=item_form)

# ADD INGREDIENT TO INGREDIENT TABLE FROM INGREDIENT PAGE
@app.route('/add_item', methods=['POST'])
def add_item():

    #initialize form for add ingredient
    item_form = ItemForm(request.form)

    db = get_db()
    cur = db.cursor()

    #fetch categories for dropdown
    cur.execute("""
        SELECT category_name
        FROM category
        ORDER BY category_name;
    """)
    categories = [("", "Select a Category")] + [(row["category_name"], row["category_name"]) for row in cur.fetchall()]
    item_form.category.choices = categories

    #fetch macros for checkboxes
    cur.execute("SELECT id, macro_name FROM macronutrient ORDER BY macro_name;")
    macros = [(row["id"], row["macro_name"]) for row in cur.fetchall()]
    item_form.macros.choices = macros

    # fetch ingredient list with categories
    cur.execute("""
        SELECT ingredient.id, ingredient.ingredient_name AS ingredient, category.category_name AS category
        FROM ingredient
        JOIN category ON ingredient.category_id = category.id
        ORDER BY category.category_name;
    """)
    ingredientInventory = cur.fetchall()

    # allows for wtforms error messages on validation failure
    if not item_form.validate_on_submit():
        return render_template('ingredient.html', ingredientInventory=ingredientInventory, item_form=item_form)
    
    # retrieve form inputs
    item_name = item_form.item.data.strip()
    category_name = item_form.category.data 
    selected_macros = item_form.macros.data 

    # fetch categories
    cur.execute("SELECT id FROM category WHERE category_name = ?", (category_name,))
    category = cur.fetchone()
        
    # if selected category doesn't exist in database, error message
    if category is None:
        item_form.category.errors.append("You must choose a valid category.") 
        return render_template('ingredient.html', ingredientInventory=ingredientInventory, item_form=item_form)
    
    category_id = category[0] #get id

    # fetch ingredients
    cur.execute("SELECT id FROM ingredient WHERE ingredient_name = ? AND category_id = ?", (item_name, category_id))
    existing_ingredient = cur.fetchone()

    # if selected ingredient already exists in database, error message
    if existing_ingredient:
        item_form.item.errors.append(f"'{item_name}' already exists in the database.") 
        return render_template('ingredient.html', ingredientInventory=ingredientInventory, item_form=item_form)
    
    # if all checks passed, insert ingredient into table
    cur.execute('INSERT INTO ingredient (ingredient_name, category_id) VALUES (?,?)', (item_name, category_id))
    ingredient_id = cur.lastrowid  # get id of new item
    db.commit()

    # if all checks passed, insert macros into junction table
    for macro_id in selected_macros:
        cur.execute("INSERT INTO ingredient_macronutrient (ingredient_id, macronutrient_id) VALUES (?, ?)", (ingredient_id, macro_id))
        db.commit()
    
    # redirect to ingredient page after submission
    return redirect(url_for('ingredientpage'))

# loads edit form for inventory item
@app.route('/inventory/update/<int:inventory_id>', methods=['GET'])
def edit_inventory(inventory_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    db = get_db()
    cur = db.cursor()
    user_id = session.get('user_id')

    # fetch inventory item details for current user
    cur.execute("""
        SELECT inventory.id, inventory.ingredient_id, ingredient.ingredient_name, 
               category.category_name, inventory.quantity
        FROM inventory
        JOIN ingredient ON inventory.ingredient_id = ingredient.id
        JOIN category ON ingredient.category_id = category.id
        WHERE inventory.id = ? AND inventory.user_id = ?
    """, (inventory_id, user_id))

    inventory_item = cur.fetchone()
    
    # if item doesn't exist, return to inventory page
    if not inventory_item:
        return redirect(url_for('index'))

    # dict for easy attribute reference
    inventory_dict = {
        "id": inventory_item["id"],
        "ingredient_id": inventory_item["ingredient_id"],
        "ingredient_name": inventory_item["ingredient_name"],
        "category_name": inventory_item["category_name"],
        "quantity": inventory_item["quantity"],
    }

   # fetch all macro from db for checkbox options
    cur.execute("SELECT id, macro_name FROM macronutrient ORDER BY macro_name;")
    all_macros = [(str(row["id"]), row["macro_name"]) for row in cur.fetchall()]

    # fetch macros currently assigned to this ingredient
    cur.execute("""
        SELECT macronutrient.id
        FROM ingredient_macronutrient
        JOIN macronutrient ON ingredient_macronutrient.macronutrient_id = macronutrient.id
        WHERE ingredient_macronutrient.ingredient_id = ?
    """, (inventory_item["ingredient_id"],))
    
    selected_macros = [str(row["id"]) for row in cur.fetchall()] 

    # fetch categories from db for dropdown
    cur.execute("SELECT category_name FROM category ORDER BY category_name;")
    categories = [("", "Select a Category")] + [(row["category_name"], row["category_name"]) for row in cur.fetchall()]

    # fetch all inventory data for table while editing item
    cur.execute("""
        SELECT inventory.id, 
               ingredient.ingredient_name AS ingredient,
               category.category_name AS category, 
               inventory.quantity, 
               inventory.last_updated,
               GROUP_CONCAT(macronutrient.macro_name, ', ') AS macros
        FROM inventory
        JOIN ingredient ON inventory.ingredient_id = ingredient.id
        JOIN category ON ingredient.category_id = category.id
        LEFT JOIN ingredient_macronutrient ON ingredient.id = ingredient_macronutrient.ingredient_id
        LEFT JOIN macronutrient ON ingredient_macronutrient.macronutrient_id = macronutrient.id
        WHERE inventory.user_id = ?
        GROUP BY inventory.id, ingredient.ingredient_name, category.category_name, inventory.quantity, inventory.last_updated
        ORDER BY inventory.last_updated DESC;
    """, (user_id,))
    full_inventory_list = cur.fetchall()
        
    # initialize and prefill the update form
    update_form = UpdateForm()
    update_form.new_name.data = inventory_dict['ingredient_name']
    update_form.quantity.data = inventory_dict['quantity']
    update_form.ingredient_id.data = inventory_dict["ingredient_id"]
    update_form.macros.choices = all_macros  # set available macros
    update_form.macros.data = selected_macros  # prefill
    update_form.new_category.choices = categories
    update_form.new_category.data = inventory_item['category_name']

    # initialize blank inventory form for homepage to preserve ui
    inventory_form = InventoryForm() 

    # render inventory page on submission
    return render_template('index.html', 
                           update_form=update_form, 
                           inventory_form=inventory_form, 
                           inventory=inventory_dict, 
                           user_inventory=full_inventory_list, 
                           selected_inventory_id=inventory_id)


# update inventory item details
@app.route('/inventory/update/<int:inventory_id>', methods=['POST'])
def update_inventory(inventory_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    db = get_db()
    cur = db.cursor()
    user_id = session.get('user_id')

    update_form = UpdateForm(request.form)

    # fetch and set category choices
    cur.execute("SELECT id, category_name FROM category ORDER BY category_name;")
    categories = [(row["category_name"], row["category_name"]) for row in cur.fetchall()]
    update_form.new_category.choices = [("", "Select a Category")] + categories

    # fetch and set macro choices
    cur.execute("SELECT id, macro_name FROM macronutrient ORDER BY macro_name;")
    macros = [(str(row["id"]), row["macro_name"]) for row in cur.fetchall()]
    update_form.macros.choices = macros

    # fetch details for existing inventory item
    cur.execute("""
        SELECT inventory.ingredient_id, ingredient.ingredient_name, category.category_name, inventory.quantity
        FROM inventory
        JOIN ingredient ON inventory.ingredient_id = ingredient.id
        JOIN category ON ingredient.category_id = category.id
        WHERE inventory.id = ? AND inventory.user_id = ?
    """, (inventory_id, user_id))

    inventory_item = cur.fetchone()

    #if item doesn't exist, reload
    if not inventory_item:
        return redirect(url_for('index'))

    ingredient_id = inventory_item["ingredient_id"]  # get ingredient_id

    # if form doesn't validate, render with errors
    if not update_form.validate_on_submit():
        print("validation failed")
        print(update_form.errors)

        # fetch user's full inventory to display table on validation error render
        cur.execute("""
            SELECT inventory.id, ingredient.ingredient_name AS ingredient,
                   category.category_name AS category, inventory.quantity, inventory.last_updated
            FROM inventory
            JOIN ingredient ON inventory.ingredient_id = ingredient.id
            JOIN category ON ingredient.category_id = category.id
            WHERE inventory.user_id = ?
            ORDER BY inventory.last_updated DESC;
        """, (user_id,))
        full_inventory_list = cur.fetchall()

        return render_template('index.html', update_form=update_form, 
                               selected_inventory_id=inventory_id, 
                               user_inventory=full_inventory_list,
                               inventory_form=InventoryForm())

    # get user input from form
    new_ingredient_name = update_form.new_name.data.strip().lower()
    new_quantity = update_form.quantity.data.strip().lower()
    new_category_name = update_form.new_category.data
    selected_macros = update_form.macros.data  

    # fetch category id for updated category
    cur.execute("SELECT id FROM category WHERE category_name = ?", (new_category_name,))
    category = cur.fetchone()
    new_category_id = category["id"]

    # fetch existing ingredient names
    cur.execute("SELECT id FROM ingredient WHERE ingredient_name = ? AND id != ?", (new_ingredient_name, ingredient_id))
    existing_ingredient = cur.fetchone()

    # if new ingredient name already exists, render error message
    if existing_ingredient:
        update_form.new_name.errors.append(f"Ingredient '{new_ingredient_name}' already exists. Choose a different name.")
        return render_template('index.html', update_form=update_form, selected_inventory_id=inventory_id)

    # once all checks pass, update ingredient name & category in ingredient table
    cur.execute("""
        UPDATE ingredient 
        SET ingredient_name = ?, category_id = ? 
        WHERE id = ?
    """, (new_ingredient_name, new_category_id, ingredient_id))

    # AND update ingredient category and quantity in inventory
    cur.execute("""
        UPDATE inventory 
        SET quantity = ?, category_id = ?, last_updated = CURRENT_TIMESTAMP 
        WHERE id = ? AND user_id = ?
    """, (new_quantity, new_category_id, inventory_id, user_id))

    # remove old macros for an item
    ##(edit form prefills previous macros, so if user doesn't explicitly change them, they will be added back)
    # because check boxes this is best method to update
    cur.execute("DELETE FROM ingredient_macronutrient WHERE ingredient_id = ?", (ingredient_id,))

    # isert new macros
    if selected_macros:
        cur.executemany(
            "INSERT INTO ingredient_macronutrient (ingredient_id, macronutrient_id) VALUES (?, ?)",
            [(ingredient_id, macro_id) for macro_id in selected_macros]
        )

    db.commit()

    return redirect(url_for('index'))

## delete inventory entry
@app.route('/inventory/delete/<int:inventory_id>', methods=['POST'])
def delete_inventory(inventory_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    db = get_db()
    cur = db.cursor()

    # find inventory item associated with user
    cur.execute("SELECT id FROM inventory WHERE id = ? AND user_id = ?", (inventory_id, session['user_id']))
    inventory_item = cur.fetchone()

    if not inventory_item:
        return redirect(url_for('index'))

    # delete it
    cur.execute("DELETE FROM inventory WHERE id = ? AND user_id = ?", (inventory_id, session['user_id']))
    db.commit()

    return redirect(url_for('index'))

#fetch ingredient table data and set up form for editing ingredient
@app.route('/update/<int:ingredient_id>', methods=['GET'])
def edit_ingredient(ingredient_id):
    db = get_db()
    cur = db.cursor()

    # get ingredient info for table
    cur.execute("""
        SELECT ingredient.id, ingredient.ingredient_name AS ingredient, category.category_name AS category
        FROM ingredient
        JOIN category ON ingredient.category_id = category.id
        ORDER BY category.category_name;
    """)
    ingredientInventory = cur.fetchall()
    
    #fetch macros from db for checkboxes
    cur.execute("SELECT id, macro_name FROM macronutrient ORDER BY macro_name;")
    macros = [(row["id"], row["macro_name"]) for row in cur.fetchall()]

    #get categories from db for dropdown
    cur.execute("SELECT category_name FROM category ORDER BY category_name;")
    categories = [("", "Select a Category")] + [(row["category_name"], row["category_name"]) for row in cur.fetchall()]

    #initialize form for ingredient input
    item_form = ItemForm()
    item_form.category.choices = categories
    item_form.macros.choices = macros

    #initilize form for updating ingredients
    update_form = UpdateForm()
    cur.execute("""
        SELECT ingredient.ingredient_name, category.category_name 
        FROM ingredient
        JOIN category ON ingredient.category_id = category.id
        WHERE ingredient.id = ?
    """, (ingredient_id,))

    ingredient = cur.fetchone()

    #prefill form
    if ingredient:
        update_form.ingredient_id.data = ingredient_id
        update_form.new_name.data = ingredient["ingredient_name"]
        update_form.new_category.choices = categories
        update_form.new_category.data = ingredient["category_name"] 

    #render ingredient page with prefilled update form
    return render_template('ingredient.html', ingredientInventory=ingredientInventory, item_form=item_form, update_form=update_form, selected_ingredient_id=ingredient_id)

#update ingredients via updateform
@app.route('/update/<int:ingredient_id>', methods=['POST'])
def update_ingredient(ingredient_id):

    # initialize form with input data
    update_form = UpdateForm(request.form)
    
    db = get_db()
    cur = db.cursor()

    # get categories from db for dropdown
    cur.execute("""
        SELECT category_name
        FROM category
        ORDER BY category_name;
    """)
    categories = [("", "Select a Category")] + [(row["category_name"], row["category_name"]) for row in cur.fetchall()]
    update_form.new_category.choices = categories

    # if form fails validation, redirect to edit page
    if not update_form.validate_on_submit():
        return redirect(url_for('edit_ingredient', ingredient_id=ingredient_id))
    
    # ensure new ingredient is cleaned for database to avoid duplicates in future
    new_name = update_form.new_name.data.strip().lower()
    new_category_name = update_form.new_category.data
    
    #validate category
    cur.execute("SELECT id FROM category WHERE category_name = ?", (new_category_name,))
    category = cur.fetchone()
    
    if category is None:
        return redirect(url_for('ingredientpage'))  

    new_category_id = category[0] #get id

    #check if new name already exists in db
    cur.execute("SELECT ingredient_name, category_id FROM ingredient WHERE id = ?", (ingredient_id,))
    current_ingredient = cur.fetchone()
    
    if not current_ingredient:
        return redirect(url_for('ingredientpage'))
    
    current_name, current_category_id = current_ingredient
    
    #if all condition met, update name/cat
    cur.execute("UPDATE ingredient SET ingredient_name = ?, category_id = ? WHERE id = ?", (new_name, new_category_id, ingredient_id))
    db.commit()

    return redirect(url_for('ingredientpage')) 

@app.route('/delete/<int:ingredient_id>', methods=['POST'])
def delete_ingredient(ingredient_id):
    db = get_db()
    cur = db.cursor()
    
    #delete from db using primary key
    cur.execute("DELETE FROM ingredient WHERE id = ?", (ingredient_id,))
    db.commit()

    return redirect(url_for('ingredientpage')) 

## api integration to get recipes for inventory items
@app.route('/get_recipes')
def get_recipes():
    if 'username' not in session:
        return redirect(url_for('login'))

    db = get_db()
    cur = db.cursor()

    # fetch all items in user inventory
    cur.execute("SELECT ingredient.ingredient_name FROM inventory JOIN ingredient ON inventory.ingredient_id = ingredient.id WHERE inventory.user_id = ?", (session['user_id'],))
    ingredients = [row["ingredient_name"] for row in cur.fetchall()]

    if not ingredients:
        return render_template('recipes.html', error="Your inventory is empty. Add ingredients first!")

    # ingredients must be a comma separated list for search
    ingredient_list = ",".join(ingredients)

    # API request -- get recipes by ingredients
    api_url = f"https://api.spoonacular.com/recipes/findByIngredients?ingredients={ingredient_list}&number=5&apiKey={SPOONACULAR_API_KEY}"
    response = requests.get(api_url)

    if response.status_code == 200:
        recipes = response.json()
        return render_template('recipes.html', recipes=recipes)
    else:
        return render_template('recipes.html', error="Failed to fetch recipes. Please try again later.")

if __name__ == '__main__':
    app.run(debug=True)