class PlayerState:
    def __init__(self, start_x=2, start_y=2):
        self.x = start_x
        self.y = start_y

    @property
    def pos(self):
        return [self.x, self.y]

    def get_new_position(self, direction, map_width, map_height):
        """Retorna [x, y] calculado para la dirección dada, o None si la tecla no es de movimiento."""
        if direction == "w":
            return [self.x, max(0, self.y - 1)]
        if direction == "s":
            return [self.x, min(map_height - 1, self.y + 1)]
        if direction == "a":
            return [max(0, self.x - 1), self.y]
        if direction == "d":
            return [min(map_width - 1, self.x + 1), self.y]
        return None

    def apply_move(self, new_pos):
        self.x, self.y = new_pos[0], new_pos[1]
