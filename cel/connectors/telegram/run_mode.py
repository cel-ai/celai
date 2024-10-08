class RunMode:
    """
    A class to represent the different modes of running a Telegram connector.

    Attributes:
    -----------
    WEBHOOK : str
        A constant representing the webhook mode.
    POLLING : str
        A constant representing the polling mode.

    Methods:
    --------
    get_modes():
        Returns a list of all available run modes.
    is_valid(mode: str):
        Checks if the provided mode is a valid run mode.
    get_mode(mode: str):
        Returns the mode if it is valid, otherwise raises an exception.
    get_default():
        Returns the default run mode.
    """

    WEBHOOK = "webhook"
    POLLING = "polling"

    @staticmethod
    def get_modes():
        """
        Returns a list of all available run modes.

        Returns:
            list: A list containing all available run modes.
        """
        return [RunMode.WEBHOOK, RunMode.POLLING]

    @staticmethod
    def is_valid(mode: str):
        """
        Checks if the provided mode is a valid run mode.

        Parameters:
            mode (str): The mode to be checked.

        Returns:
            bool: True if the mode is valid, False otherwise.
        """
        return mode in RunMode.get_modes()

    @staticmethod
    def get_mode(mode: str):
        """
        Returns the mode if it is valid, otherwise raises an exception.

        Parameters:
            mode (str): The mode to be returned.

        Returns:
            str: The valid mode.

        Raises:
            Exception: If the mode is not valid.
        """
        if RunMode.is_valid(mode):
            return mode
        else:
            raise Exception(f"Invalid run mode: {mode}. Valid modes are: {RunMode.get_modes()}")

    @staticmethod
    def get_default():
        """
        Returns the default run mode.

        Returns:
            str: The default run mode.
        """
        return RunMode.WEBHOOK