# Estimates achievable timelines and milestones.

import re
import sys
from collections import defaultdict

def parse_input(input_file):
    """Parse the input file and return a list of tuples."""
    lines = []
    with open(input_file, 'r') as f:
        for line in f:
            lines.append(line.strip())
    return lines

def extract_numbers(text):
    """Extract numbers from text."""
    numbers = re.findall(r'\d+', text)
    return [int(num) for num in numbers]

def calculate_timeline(lines):
    """Calculate the timeline."""
    timeline = defaultdict(int)
    for line in lines:
        numbers = extract_numbers(line)
        if numbers:
            timeline[line] = numbers[0]
    return timeline

def main(input_file):
    """Main function."""
    lines = parse_input(input_file)
    timeline = calculate_timeline(lines)
    print(timeline)

if __name__ == '__main__':
    input_file = sys.argv[1]
    main(input_file)