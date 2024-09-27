from flask import current_app
from itsdangerous import URLSafeTimedSerializer


def generateToken(email):
    """
    Generate a token used to confirm a user email.

    Args:
        email (str): The email address to confirm.

    Returns:
        The token.
    """
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return serializer.dumps(
        email, salt=current_app.config["SECURITY_PASSWORD_SALT"]
    )


def confirmToken(token, expiration=3600):
    """
    Given a token, determine whether it is valid or not.

    Args:
        token (str): The token.
        expiration (int): The time for which the token is valid in 
            seconds. Default = 3600 (1 hour).

    Returns:
        email (str | bool): The validated email or False if the token
            was expired.
    """
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    try:
        email = serializer.loads(
            token,
            salt=current_app.config["SECURITY_PASSWORD_SALT"],
            max_age=expiration
        )
    except:
        return False
    return email
