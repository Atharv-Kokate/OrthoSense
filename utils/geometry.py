import numpy as np

def calculate_angle(a, b, c):
    """
    Calculate the angle between three points a, b, c (where b is the vertex).
    Points should be in format (x, y) or [x, y].
    Returns angle in degrees.
    """
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    
    # Vectors
    ba = a - b
    bc = c - b
    
    # Calculate cosine of angle
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    
    # Clip to avoid numerical errors outside [-1, 1] before arccos
    angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
    
    return np.degrees(angle)
