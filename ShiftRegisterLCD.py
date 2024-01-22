import time

class LCD:
    def __init__(self, register_data, register_clock,
                 register_clear, lcd_clock, lcd_mode_sel):
        self.__lcd_enable = lcd_clock
        self.__lcd_rs = lcd_mode_sel
        self.__register_data = register_data
        self.__register_clear = register_clear
        self.__register_enable = register_clock

        self.__writeReg(0x38)
        self.setCursorMode()
        self.setEntryMode()

    def home(self) -> None:
        """
        Sets the cursor to 0, 0
        """
        self.__setMode()
        self.__writeReg(0x2)

    def clear(self) -> None:
        """
        Clears the whole display.
        """
        self.__setMode()
        self.__writeReg(0x1)
    
    def setEntryMode(self, direction: bool = True,
                     display: bool = False) -> None:
        """
        The direction argument sets whether the cursor moves left or
        right after displaying a character. (Setting it True moves 
        the cursor to the right)

        The display argument sets whether the cursor or the display
        moves. (Setting it True moves the display)
        
        Default cursor to the right, static display.
        """

        self.__setMode()
        if direction:
            if display:
                self.__writeReg(0x7)
            else:
                self.__writeReg(0x6)
        else:
            if display:
                self.__writeReg(0x5)
            else:
                self.__writeReg(0x4)

    def write(self, string: str):
        """Displays the given string input."""

        if len(string) > 16:
            raise ValueError("Text length exceded 16 characters by {}."
                             .format(len(string) - 16))
        if len(string) <= 0:
            raise ValueError("Cannot display an empty string.")

        self.__setMode(True)
        for character in string:
            self.__writeReg(ord(character))
    
    def setCursor(self, x: int, y: int) -> None:
        """
        Sets the cursor to the given position.

        The starting position is in the top left corner (0,0)
        """
        
        if not (0 <= x <= 15 and 0 <= y <= 1):
            raise IndexError("Parameters X ({}) or Y ({}) are out of range."
                             .format(x, y))

        self.__setMode()
        self.__writeReg(0x80 + x + (0x40 if y == 1 else 0))

    def setCursorMode(self, active: bool = False, blink: bool = False) -> None:
        """
        Sets the state of the cursor.
        When blink is True, active is automaticaly set to True.
        """
        self.__setMode()
        if blink:
            self.__writeReg(0xf)
            return
        if active:
            self.__writeReg(0xe)
            return
        self.__writeReg(0xc)


    def displayOff(self) -> None:
        """Turn off the display."""

        self.__setMode()
        self.__writeReg(0x8)

    def shiftCursorLeft(self, step: int = 1) -> None:
        """
        Shifts the cursor to the left by the given amount.

        Default 1.
        """

        self.__setMode()
        for _ in range(step):
            self.__writeReg(0x10)

    def shiftCursorRight(self, step: int = 1) -> None:
        """
        Shifts the cursor to the right by the given amount.

        Default 1.
        """

        self.__setMode()
        for _ in range(step):
            self.__writeReg(0x14)
    
    def shiftDisplayLeft(self, step: int = 1) -> None:
        """
        Shifts the display to the left by the given amount.

        Default 1.
        """

        self.__setMode()
        for _ in range(step):
            self.__writeReg(0x18)

    def shiftDisplayRight(self, step: int = 1) -> None:
        """
        Shifts the display to the right by the given amount.

        Default 1.
        """

        self.__setMode()
        for _ in range(step):
            self.__writeReg(0x1C)


    def __writeReg(self, data: int) -> None:
        """
        Sets the shift register's data to the input number's binary
        representative before submitting to the lcd.
        """

        self.__clearReg()
        self.__register_enable.off()
        for _ in range(8):
            self.__register_data.value(data & 0x01)
            self.__register_enable.on()
            self.__register_enable.off()
            data >>= 1
        self.__register_enable.on()
        self.__register_enable.off()
        time.sleep_ms(1)
        self.__lcd_enable.on()
        self.__lcd_enable.off()
        time.sleep_ms(1)
    
    def __clearReg(self) -> None:
        """Clears the shift register"""

        self.__register_clear.off()
        for _ in range(10):
            self.__register_data.value(0)
            self.__register_enable.on()
            self.__register_enable.off()
        self.__register_clear.on()
        time.sleep_ms(1)
    
    def __setMode(self, mode: bool = False) -> None:
        """When set to low, the LCD is in Command mode."""

        self.__lcd_rs.value(mode)
