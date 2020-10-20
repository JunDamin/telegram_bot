import logging


def _generate_log(path):
    """
    Create a logger object
    :param path: Path of the log file.
    :return: Logger object.
    """
    # Create a logger and set the level.
    logger = logging.getLogger("Log_info")
    # Check handler exists
    if len(logger.handlers) > 0:
        return logger  # Logger already exists
    # set logger level
    logger.setLevel(logging.DEBUG)
    # Create file handler, log format and add the format to file handler
    stream_handler = logging.StreamHandler()
    file_handler = logging.FileHandler(path)

    # See https://docs.python.org/3/library/logging.html#logrecord-attributes
    # for log format attributes.
    log_format = "%(levelname)s %(asctime)s %(message)s"
    formatter = logging.Formatter(log_format)
    stream_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

    return logger


def log_info(path="log_info.log"):
    """
    We create a parent function to take arguments
    :param path:
    :return:
    """

    def info_log(func):
        def wrapper(*args, **kwargs):

            try:
                # Execute the called function, in this case `divide()`.
                # If it throws an error `Exception` will be called.
                # Otherwise it will be execute successfully.
                logger = _generate_log(path)
                update = args[0]
                user = update.message.from_user
                user_data = args[1].user_data
                logger.info(
                    f"m_status: {user_data.get('status')}, log id: {user_data.get('log_id')}, {user.id} {user.first_name} {user.last_name} reply '{update.message.text}', run {func.__name__}"
                )
                return func(*args, **kwargs)
            except Exception as e:
                logger = _generate_log(path)
                error_msg = f"And error has occurred at {func.__name__}"
                logger.exception(error_msg)

                return e  # Or whatever message you want.

        return wrapper

    return info_log


def write_info_log(text: str, path="log_info.log"):
    logger = _generate_log(path)
    logger.info(text)
