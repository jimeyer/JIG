"""Module demonstrating inheritance."""


class Animal:
    """Base animal class."""

    def speak(self):
        """Make a sound."""
        pass


class Dog(Animal):
    """A dog is an animal."""

    def speak(self):
        """Dogs bark."""
        return "Woof!"

    def fetch(self):
        """Dogs fetch."""
        return "Fetching..."


class Cat(Animal):
    """A cat is an animal."""

    def speak(self):
        """Cats meow."""
        return "Meow!"


class Robot:
    """A robot (not an animal)."""

    def beep(self):
        """Robots beep."""
        return "Beep boop!"


class RobotDog(Robot, Dog):
    """Multiple inheritance example."""

    def charge(self):
        """Robot dogs need charging."""
        return "Charging..."
