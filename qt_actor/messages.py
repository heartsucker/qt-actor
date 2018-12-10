class StopType:

    """
    Message type that will cause an actor to exit when sent an instance of this class, even with a
    non-empty inbox.
    """

    __INSTANCE = None

    def __new__(cls):
        if StopType.__INSTANCE is None:
            StopType.__INSTANCE = super().__new__(cls)
        return StopType.__INSTANCE

    def __repr__(self) -> str:
        return 'Stop'


Stop = StopType()
Stop.__doc__ = "Message type that will cause and actor to exit, even with a non-empty inbox."
