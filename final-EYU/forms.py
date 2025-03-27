from flask_wtf import FlaskForm
from flask_bcrypt import check_password_hash
from wtforms import StringField, SubmitField, SelectField, HiddenField, PasswordField, SelectMultipleField, widgets
from wtforms.validators import DataRequired, Email, Length, Regexp, EqualTo, ValidationError, Optional
import sqlite3

def get_db():
    db = sqlite3.connect("inventory.db")
    db.row_factory = sqlite3.Row
    return db

class ItemForm(FlaskForm):
    item = StringField("Add Item", validators=[DataRequired(message="There is nothing to add!"), Length(min=2, max=50, message="Hmm, not sure if that's an item.")])
    category = SelectField("Category", choices=[("", "Select a Category")], validators=[DataRequired(message="Please select a category!")])
    macros = SelectMultipleField("Macronutrients", coerce=int, option_widget=widgets.CheckboxInput(), widget=widgets.ListWidget(prefix_label=False))
    submit = SubmitField("Add")

class UpdateForm(FlaskForm):
    ingredient_id = HiddenField("Ingredient ID")
    new_name = StringField("New Name", validators=[DataRequired(), Length(min=2, max=50)])
    new_category = SelectField("New Category", choices=[("", "Select a Category")], validators=[DataRequired(message="Please select a category!")])
    quantity = StringField('Quantity', validators=[Optional()])
    macros = SelectMultipleField('Macros', validators=[Optional()])
    submit = SubmitField("Update")

    def validate_new_name(self, field):
        db = get_db()
        cur = db.cursor()

        ingredient_id = self.ingredient_id.data 

        # does name already exist in db
        cur.execute("""
            SELECT id FROM ingredient WHERE ingredient_name = ? AND id != ?
        """, (field.data.strip().lower(), ingredient_id))

        existing_ingredient = cur.fetchone()

        if existing_ingredient:
            raise ValidationError(f"Ingredient '{field.data}' already exists.")


class DeleteForm(FlaskForm):
    submit = SubmitField("Delete")

class CreateUserForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(message="Username required."), Length(min=3, max=32)])
    email = StringField("Email", validators=[DataRequired(message="Email address required."), Email(message="Please enter a valid email address.")])
    password = PasswordField("Password", validators=[DataRequired(message="Password required."), Regexp(r"^(?:(?=.*[a-z])(?:(?=.*[A-Z])(?=.*[\d\W])|(?=.*\W)(?=.*\d))|(?=.*\W)(?=.*[A-Z])(?=.*\d)).{8,32}$", message = "Password must be between 8 and 32 characters and include a lowercase letter, an uppercase letter, a number, and an non-alphanumeric character."), EqualTo('confirm', message='Passwords must match.')])
    confirm = PasswordField("Confirm Password")
    submit = SubmitField("Create Account")

    def validate_username(self, username):
        db =get_db()
        cur = db.cursor()
        cur.execute("SELECT id FROM user WHERE username =?", (username.data,))
        user = cur.fetchone()
        db.close()
        if user:
            raise ValidationError("Username already associated with an account.")
        
    def validate_email(self, email):
        db =get_db()
        cur = db.cursor()
        cur.execute("SELECT id FROM user WHERE email =?", (email.data,))
        user = cur.fetchone()
        db.close()
        if user:
            raise ValidationError("Email already associated with an account.")
        
class LoginForm(FlaskForm):
    login_field = StringField("Username or Email", validators=[DataRequired(message="Username or Email required.")])
    password = PasswordField("Password", validators=[DataRequired(message="Password required.")])
    submit = SubmitField("Login")

    user=None

    def validate_login_field(self, login_field):

        db = get_db()
        cur = db.cursor()
        
        # get username and password from db
        cur.execute("SELECT * FROM user WHERE username = ? OR email = ?", (login_field.data, login_field.data))
        user = cur.fetchone()

        if not user:
            raise ValidationError("Invalid username or email.") 
        # store user ID
        self.user = user

     
    def validate_password(self, password):
        
        if self.user is None:
            return

        if not check_password_hash(self.user["hashed_password"], password.data):
            raise ValidationError("Incorrect password.") 

class InventoryForm(FlaskForm):
    ingredient = StringField("Add Ingredient", validators=[DataRequired(message="There is nothing to add!"), Length(min=2, max=50, message="Hmm, not sure if that's an item.")])
    quantity = StringField("Quantity", validators=[DataRequired(message="Enter a quantity.")])
    submit = SubmitField("Add")

class InventoryItemForm(FlaskForm):
    item = StringField("Add Item", validators=[DataRequired(message="There is nothing to add!"), Length(min=2, max=50, message="Hmm, not sure if that's an item.")])
    category = SelectField("Category", choices=[("", "Select a Category")], validators=[DataRequired(message="Please select a category!")])
    macros = SelectMultipleField("Macronutrients", coerce=int, option_widget=widgets.CheckboxInput(), widget=widgets.ListWidget(prefix_label=False))
    quantity = StringField("Quantity", validators=[DataRequired(message="Enter a quantity.")])
    submit = SubmitField("Add")