import pulumi


class OutputFactory:
    """
    Convenient wrapper around Output madness
    """

    def __new__(cls, val):
        return pulumi.Output.from_input(val)
