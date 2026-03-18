class Car:
    """
    Represents a single EV on the road.
 
    Attributes:
        journey_duration_minutes: How long the car will stay on the road.
        remaining_minutes:        Minutes left until the journey ends.
    """
 
    def __init__(self, journey_duration_minutes: int):
        self.journey_duration_minutes = journey_duration_minutes
        self.remaining_minutes = journey_duration_minutes
 
    def tick(self, minutes: int) -> None:
        """Age the car by the given number of minutes."""
        self.remaining_minutes -= minutes
 
    @property
    def has_finished(self) -> bool:
        return self.remaining_minutes <= 0