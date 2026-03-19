import json

from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import (
    BooleanField,
    FloatField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    InputRequired,
    Length,
    NumberRange,
    Optional,
    ValidationError,
)


def validate_json_object(form, field):
    raw_value = (field.data or "").strip()
    if not raw_value:
        return

    try:
        parsed = json.loads(raw_value)
    except json.JSONDecodeError as exc:
        raise ValidationError(f"Invalid JSON: {exc.msg}") from exc

    if not isinstance(parsed, dict):
        raise ValidationError("Value must be a JSON object.")

    if field.name == "category_multipliers_json":
        for key, value in parsed.items():
            if not isinstance(value, (int, float)) or value < 0:
                raise ValidationError(f"Multiplier for '{key}' must be a non-negative number.")


class RegisterForm(FlaskForm):
    display_name = StringField("Display Name", validators=[DataRequired(), Length(max=100)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=255)])
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=8, max=128, message="Password must be at least 8 characters long."),
        ],
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[DataRequired(), EqualTo("password")],
    )
    preference_mode = SelectField(
        "Preference Mode",
        choices=[("travel", "Travel"), ("cashback", "Cash Back")],
        default="travel",
    )
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=255)])
    password = PasswordField("Password", validators=[DataRequired(), Length(max=128)])
    submit = SubmitField("Log In")


class UploadTransactionsForm(FlaskForm):
    data_file = FileField(
        "Transaction File",
        validators=[
            FileRequired(),
            FileAllowed(["csv", "json"], "Upload a CSV or JSON file."),
        ],
    )
    submit = SubmitField("Upload Transactions")


class CardForm(FlaskForm):
    card_id = StringField("Card ID", validators=[DataRequired(), Length(max=50)])
    name = StringField("Card Name", validators=[DataRequired(), Length(max=100)])
    issuer = StringField("Issuer", validators=[DataRequired(), Length(max=50)])
    annual_fee = FloatField("Annual Fee", validators=[InputRequired(), NumberRange(min=0)])
    base_reward_rate = FloatField("Base Reward Rate", validators=[InputRequired(), NumberRange(min=0)])
    credit_utilization_rate = FloatField(
        "Credit Utilization Rate",
        validators=[InputRequired(), NumberRange(min=0)],
    )
    category_multipliers_json = TextAreaField(
        "Category Multipliers JSON",
        validators=[Optional(), validate_json_object],
    )
    credits_json = TextAreaField("Credits JSON", validators=[Optional(), validate_json_object])
    transfer_partners_json = TextAreaField(
        "Transfer Partners JSON",
        validators=[Optional(), validate_json_object],
    )
    category_caps_json = TextAreaField(
        "Category Caps JSON",
        validators=[Optional(), validate_json_object],
    )
    is_active = BooleanField("Active", default=True)
    submit = SubmitField("Save Card")

