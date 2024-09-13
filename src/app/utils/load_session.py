from PyQt5.QtCore import QSettings


def load_session():
    settings = QSettings("Enaplic", "EurekaApp")
    user_data = {
        "full_name": settings.value("full_name"),
        "username": settings.value("username"),
        "email": settings.value("email"),
        "role": settings.value("role")
    }
    if user_data["username"]:
        return user_data
    else:
        return None
