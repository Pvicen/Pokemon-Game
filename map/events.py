def check_collision(player_pos, objects):
    """Returns the first object at player_pos, or None if the cell is free."""
    for obj in objects:
        if obj["x"] == player_pos[0] and obj["y"] == player_pos[1]:
            return obj
    return None
