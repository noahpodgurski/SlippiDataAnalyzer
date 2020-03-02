# Checks whether this is a damaged state
def is_damaged(state):
    return 75 <= state <= 91

# Checks whether this is a grabbed state
def is_grabbed(state):
    return 223 <= state <= 236

# Checks whether this is a teching state
def is_teching(state):
    return 199 <= state <= 204

# Checks whether this is a state in which the character is in control
def is_in_control(state):
    
    ground = 14 <= state <= 24 
    squat = 39 <= state <= 41
    ground_attack = 44 <= state <= 64
    grabbing = state == 212
    
    return ground or squat or ground_attack or grabbing

# Checks whether this is a death state
def is_dead(state):
    return 0 <= state <= 10

# Checks whether this is an attacking state
def is_attacking(state):
    return 44 <= state <= 69

# Calculates the damage taken from an attack
# NOTE: ARGUMENTS MUST BE frame.post
def damage_taken(pre_frame, post_frame):
    return post_frame.damage - pre_frame.damage

# Checks if the state is one of grabbing
def is_grabbing(state):
    return state == 212 or state == 214

# Checks if the state is holding an opponent from a successful grab
def is_holding(state):
    return state == 213 or 215 <= state <= 218

# Checks if the state is one of respawning
def is_respawn(state):
    return state == 12 or state == 13