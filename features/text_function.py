from datetime import datetime


def make_record_text(row):
    (
        log_id,
        chat_id,
        first_name,
        last_name,
        _datetime,
        category,
        sub_category,
        longitude,
        latitude,
        remarks,
        confirmation,
        work_content_id,
    ) = row
    dt = datetime.fromisoformat(_datetime)
    text_message = f"""
    {category} {"- " + sub_category if sub_category else ""}
    Log No.{log_id} : {convert_datetime_to_text(dt)}
    location : {"Reported" if longitude != "Not Available" and longitude != None else "NOT reported"}
    remarks : {remarks if remarks else "-"}\n"""

    return text_message


def convert_datetime_to_text(_datetime: datetime):
    text = _datetime.strftime("*__%m-%d__* *__%H:%M__*")

    return text


def make_text_signing_in_greeting(log_id, first_name, _datetime: datetime):
    SIGN_IN_GREETING = (
        f"""Good morning, `{first_name}`.\nYou have signed in with Log No.{log_id}"""
    )
    SIGN_TIME = f"""signing time: {_datetime.strftime("%m-%d *__%H:%M__*")}"""
    CHECK_DM = """_Please check my DM(Direct Message) to you_"""

    return f"{SIGN_IN_GREETING}\n{CHECK_DM}\n{SIGN_TIME}"


def make_text_signing_in_and_ask_info(log_id, first_name, _datetime: datetime):
    SIGN_IN_GREETING = (
        f"""Good morning, `{first_name}`.\nYou have signed in with Log No.{log_id}"""
    )
    SIGN_TIME = f"""signing time: {_datetime.strftime("%m-%d *__%H:%M__*")}"""
    ASK_INFO = """Would you like to share where you work?"""

    return f"{SIGN_IN_GREETING}\n{ASK_INFO}\n{SIGN_TIME}"
