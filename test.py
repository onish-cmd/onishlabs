import math

# A global constant to see if the AST keeps it
PI_PRECISION = 5


def get_pi():
    """Returns pi rounded to our precision."""
    return round(math.pi, PI_PRECISION)


def calculate_area(radius):
    """
    The function to refactor!
    It calls get_pi(), so the slicer should see the dependency.
    """
    pi = get_pi()
    area = pi * (radius**2)
    return area


def main():
    r = 5
    print(f"Radius: {r}")
    print(f"Area: {calculate_area(r)}")


if __name__ == "__main__":
    main()
