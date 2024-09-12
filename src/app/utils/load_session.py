from PyQt5.QtCore import QSettings


def load_session():
    settings = QSettings("Enaplic", "EurekaApp")
    user_data = {
        "username": settings.value("username"),
        "email": settings.value("email"),
        "role": settings.value("role"),
        "full_name": settings.value("full_name")
    }
    if user_data["username"]:
        return user_data
    else:
        return None
