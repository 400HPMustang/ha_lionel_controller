"""Train model definitions with announcement name mappings.

This file contains announcement name mappings for different Lionel train models.
Each train model has different voice announcements, so this allows users to see
the correct names for their specific train.

To contribute a new train model:
1. Add a new entry to TRAIN_MODELS with your train's name as the key
2. Map each announcement slot to the actual phrase your train says
3. Submit a pull request!

The announcement slots are:
- ready_to_roll
- hey_there
- squeaky
- water_and_fire
- fastest_freight
- penna_flyer
"""

# Default/Generic announcement names used when train model is unknown
DEFAULT_ANNOUNCEMENTS = {
    "random": "Random",
    "ready_to_roll": "Ready to Roll",
    "hey_there": "Hey There",
    "squeaky": "Squeaky",
    "water_and_fire": "Water & Fire",
    "fastest_freight": "Fastest Freight",
    "penna_flyer": "Penna Flyer",
}

# Train model-specific announcement mappings
# Key: Train model name shown in config flow
# Value: Dict mapping announcement keys to display names
TRAIN_MODELS = {
    "Generic": DEFAULT_ANNOUNCEMENTS,

    "Polar Express": {
        "random": "Random",
        "ready_to_roll": "Polar Express",
        "hey_there": "All Aboard",
        "squeaky": "You Coming?",
        "water_and_fire": "Tickets",
        "fastest_freight": "First Gift",
        "penna_flyer": "The King",
    },

    "Thomas The Tank Engine": {
        "random": "Random",
        "ready_to_roll": "Oh Yeah!",
        "hey_there": "All Aboard",
        "squeaky": "Full Steam Ahead!",
        "water_and_fire": "Number 1 Engine",
        "fastest_freight": "On Track and On Time!",
        "penna_flyer": "Rocking the Rails",
    },

    "Hogwarts Express": {
        "random": "Random",
        "ready_to_roll": "Here's your ticket",
        "hey_there": "Platform 9 3/4",
        "squeaky": "Ron Weasley",
        "water_and_fire": "Harry Potter",
        "fastest_freight": "Anything off the trolley",
        "penna_flyer": "Hermione Granger",
    },
}

# List of available train models for config flow
TRAIN_MODEL_OPTIONS = list(TRAIN_MODELS.keys())


def get_announcement_names(train_model: str) -> dict:
    """Get announcement name mappings for a specific train model.

    Args:
        train_model: The train model name, e.g. "Polar Express"

    Returns:
        Dict mapping announcement keys to display names
    """
    return TRAIN_MODELS.get(train_model, DEFAULT_ANNOUNCEMENTS)


def get_announcement_name(train_model: str, announcement_key: str) -> str:
    """Get a specific announcement name for a train model.

    Args:
        train_model: The train model name
        announcement_key: The announcement key, e.g. "ready_to_roll"

    Returns:
        The display name for that announcement
    """
    names = get_announcement_names(train_model)
    return names.get(
        announcement_key,
        announcement_key.replace("_", " ").title(),
    )
