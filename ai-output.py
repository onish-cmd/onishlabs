import math
PI_PRECISION = 5

def get_pi():
    """Returns pi rounded to our precision."""
    return round(math.pi, PI_PRECISION)

def calculate_area(radius: float) -> float:
    pi = get_pi()
    area = pi * math.pow(radius, 2)
    return area

def main():
    r = 5
    print(f'Radius: {r}')
    print(f'Area: {calculate_area(r)}')
if __name__ == '__main__':
    main()