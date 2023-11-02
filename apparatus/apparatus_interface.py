import abc

import apparatus.ledout as Ledout


class ApparatusInterface(metaclass=abc.ABCMeta):

    CAROUSEL_1 = 0
    CAROUSEL_2 = 1

    LEVER_TOUCH = 0
    LEVER_PULLED = 1
    LEVER_RELEASED = 2

    @abc.abstractmethod
    def init_hw(self):
        """[summary]
        Starts the initialization of the hardware components to set them to the settings defined in the configuration file.
        """
        pass

    @abc.abstractmethod
    def hw_self_test(self):
        """[summary]
        Starts a self-test routine that runs through all possible movement radii and output possibilities once in order to perform a fault diagnosis on them.
        """
        pass

    @abc.abstractmethod
    def play_sound(self, file=None, volume=90, timestamp=None):
        """[summary]
        Plays a sound file located on the server.
        See /sounds/ for available files.
        Args:
            file (string, optional): Path to the sound file that is to be played back. Defaults to None.
            volume (int, optional): The volume in percent. Defaults to 90.
            timestamp (datetime, optional): A future timestamp at which the command should be executed. Defaults to None.
        """
        pass

    @abc.abstractmethod
    def empty_human(self):
        """[summary]
        Empties the Carrussele food containers into the Human Food Dispenser.
        """
        pass

    @abc.abstractmethod
    def move_to(self, carousel_id, compartment_id, monkey=False, blocking=False):
        """[summary]
        Moves a compartment of a carousel to a defined output position.
        Args:
            carousel_id (int): The identification of the carousel to be driven
            compartment_id (int): The identification of the compartment to be placed above the output.
            monkey (bool, optional): Sets the side of the output to monkey or human side. Defaults to False.
            blocking (bool, optional): Blocks the called function until the target position is reached. Defaults to False.
        """
        pass

    @abc.abstractmethod
    def move_to_wait(self, carousel_id):
        """[summary]
        A blocking function that waits for the actions of the move_to function to finish.
        Args:
            carousel_id (int): The identification of the carousel to be driven
        """
        pass

    @abc.abstractmethod
    def deploy(self, carousel_id, compartment_id, monkey=False, blocking=False):
        """[summary]
        Moves a compartment of a carousel to a specified output position and deploys its contents.
        Args:
            carousel_id (int): The identification of the carousel to be driven
            compartment_id (int): The identification of the compartment to be placed above the output.
            monkey (bool, optional): Sets the side of the output to monkey or human side. Defaults to False.
            blocking (bool, optional): Blocks the called function until the target position is reached. Defaults to False.
        """
        pass

    @abc.abstractmethod
    def deploy_wait(self, carousel_id):
        """[summary]
        A blocking function that waits for the actions of the deploy function to finish.
        Args:
            carousel_id (int): The identification of the carousel to be driven
        """
        pass

    @abc.abstractmethod
    def set_test_light(self, state, color=Ledout.COLORS["RED"]):
        """[summary]
        Turns the test light off and on and allows to set a desired color.
        Args:
            state (bool): Sets the desired target status of the LEDs (on/off).
            color (Hexadecimal color code[int], optional): Sets a desired color. Defaults to Ledout.COLORS["RED"].
        """
        pass

    @abc.abstractmethod
    def set_human_light(self, state, color=Ledout.COLORS["RED"]):
        """[summary]
        Turns the human light off and on and allows to set a desired color.
        Args:
            state (bool): Sets the desired target status of the LEDs (on/off).
            color (Hexadecimal color code[int], optional): Sets a desired color. Defaults to Ledout.COLORS["RED"].
        """
        pass

    @abc.abstractmethod
    def set_light(self, color, timestamp=None):
        """[summary]
        Sets the device lights to a desired color.
        Args:
            color (Hexadecimal color code[int], optional): Sets a desired color. Defaults to Ledout.COLORS["RED"].
            timestamp (datetime, optional): A future timestamp at which the command should be executed. Defaults to None.
        """
        pass

    @abc.abstractmethod
    def wait_lever_state(self, pin_io, state, timeout=-1, spinlock=False):
        """[summary]
        A blocking function that blocks until a specific lever state event occurs.

        Args:
            pin_io (enum:[int] (LEVER_TOUCH, LEVER_PULLED, LEVER_RELEASED)): Specify the lever state event.
            state (boot): The status of the event being waited for.
            timeout (int, optional): A timeout in s for this function to be blocked. Defaults to -1.
            spinlock (bool, optional): Enables a spinlock for faster response, but with higher computing power consumption.. Defaults to False.
        """
        pass

    @abc.abstractmethod
    def set_lever_open(self, state, timestamp=None):
        """[summary]
        Opens and closes the lock of the lever installed in the apparatus.
        Args:
            state (bool): The state of the lock. True is open, False is closed.
            timestamp (datetime, optional): A future timestamp at which the command should be executed. Defaults to None.

        """
        pass
