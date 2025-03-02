# Python Program to convert text to GLSL for use in Complementary Shaders by @SpacEagle17
import re
import os
from typing import List, Union, Optional, Dict, Tuple

# Try to import pyperclip but don't fail if it's not available
try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False

'''
INSTRUCTIONS:

1. Create a .txt file with the following format (can repeat multiple times)):
[darken(value)]  # Optional, first line only
start(size, x, y)
vec3(r, g, b)
Text to convert
end()
2. Run the script and enter the path to the .txt file when prompted
3. The converted text will be printed to the console, saved to a new file and copied to clipboard (if available)


EXAMPLE (can be copied for testing):
darken(0.5)
start(4, 30, 30)
vec3(1, 0, 0)
BIG TITLE
end()

start(2, 0, 80)
vec3(1.0, 1.0, 1.0)
Hello my name is XYZ.
I like potatoes, very much: ok!

vec3(1, 0, 0)
AAAAAAAAAAAAAAA



vec3(1)
This is a new paragraph
. -,:_"!<>[]()=+
vec3(1.0, 0.0, 1.0)
This text has a new color
end()
END OF EXAMPLE

ALLOWED CHARACTERS:
- Alphanumeric characters
- Space, ., -, ,, :, _, ", !, >, <, [, ], (, ), =, +


COMMANDS:
- darken(value): Optional, first line only. Darkens the background. Default: 0.65 - Allowed range: 0.0 to 1.0
- start(size, x, y): Start a new text section with size and position
- vec3(r, g, b): Set the color for the text section - can be in vec3(1.0, 1.0, 1.0) or vec3(1, 1, 1) or vec3(1) format
- end(): End the current text section

'''

# Constants
DEFAULT_DARKNESS = 0.65
EMPTY_LINE_RESULT = '    printLine();'
SECTION_END_RESULT = 'endText(color.rgb);'

# Compiled regex patterns for better performance
START_PATTERN = re.compile(r'start\((\d+),\s*(\d+),\s*(\d+)\)')
COLOR_PATTERN = re.compile(r'vec3\((\d+(?:\.\d+)?)\s*(?:,\s*(\d+(?:\.\d+)?)\s*(?:,\s*(\d+(?:\.\d+)?))?)?\)')
DARKEN_PATTERN = re.compile(r'darken\((\d+(?:\.\d+)?)\)')

# Special character mapping
SPECIAL_CHARS: Dict[str, str] = {
    'space': '_space',
    'under': '_under',
    'quote': '_quote',
    'exclm': '_exclm',
    'gt': '_gt',
    'lt': '_lt',
    'opsqr': '_opsqr',
    'clsqr': '_clsqr',
    'opprn': '_opprn',
    'clprn': '_clprn',
    'block': '_block',
    'copyr': '_copyr', 
    'equal': '_equal',
    'plus': '_plus',
    'dot': '_dot',
    'minus': '_minus',
    'comma': '_comma',
    'colon': '_colon'
}

# Reverse mapping for quick lookup
CHAR_TO_SPECIAL: Dict[str, str] = {
    ' ': 'space', '.': 'dot', '-': 'minus', ',': 'comma', 
    ':': 'colon', '_': 'under', '"': 'quote', '!': 'exclm', 
    '>': 'gt', '<': 'lt', '[': 'opsqr', ']': 'clsqr', 
    '(': 'opprn', ')': 'clprn', '█': 'block', '©': 'copyr', 
    '=': 'equal', '+': 'plus'
}

def is_valid_char(char: str, is_command_line: bool = False) -> bool:
    """
    Check if character is allowed in the input text.
    
    Args:
        char: The character to check
        is_command_line: Whether the character is part of a command line
        
    Returns:
        True if the character is valid, False otherwise
    """
    return (char.isalnum() or 
            char in CHAR_TO_SPECIAL or 
            (is_command_line and char in '()'))

def convert_to_chars(text: str) -> List[str]:
    """
    Convert text to character identifiers used in the GLSL output.
    
    Args:
        text: The text to convert
        
    Returns:
        A list of character identifiers
    """
    converted_chars = []
    for char in text:
        if char.isalpha():  # Handle both upper and lowercase in one condition
            converted_chars.append(f'_{char}')
        elif char in CHAR_TO_SPECIAL:
            converted_chars.append(SPECIAL_CHARS[CHAR_TO_SPECIAL[char]])
        else:
            converted_chars.append(f'_{char}')
    return converted_chars

def validate_text(lines: List[str]) -> None:
    """
    Validate input text for allowed characters and proper structure.
    
    Args:
        lines: List of text lines to validate
        
    Raises:
        ValueError: If invalid characters or structure is found
    """
    for line_num, line in enumerate(lines, 1):
        # Check if the line is a command line
        is_command_line = (
            line.startswith('start(') or 
            line.startswith('vec3(') or 
            line == 'end()' or
            line.startswith('darken(')
        )
        
        for char in line:
            if not is_valid_char(char, is_command_line):
                raise ValueError(f"Illegal character '{char}' found on line {line_num}")

def process_darken_command(line: str) -> str:
    """
    Process darken() command and return corresponding GLSL code.
    
    Args:
        line: The darken command line
        
    Returns:
        GLSL code string for the darken effect
        
    Raises:
        ValueError: If the darken command format is invalid or value is out of range
    """
    darken_match = DARKEN_PATTERN.match(line.strip())
    if darken_match:
        # Extract darkness value if provided
        darkness = float(darken_match.group(1))
        
        # Validate range (0.0 to 1.0)
        if darkness < 0.0 or darkness > 1.0:
            raise ValueError(f"Darkness value must be between 0.0 and 1.0, got {darkness}")
            
        return f'color.rgb = mix(color.rgb, vec3(0.0), {darkness});'
    elif line.strip() == 'darken()':
        # Use default darkness value
        return f'color.rgb = mix(color.rgb, vec3(0.0), {DEFAULT_DARKNESS});'
    else:
        raise ValueError("Invalid darken() format. Use darken() or darken(value)")

def process_start_command(line: str) -> Optional[str]:
    """
    Process start() command and return corresponding GLSL code.
    
    Args:
        line: The start command line
        
    Returns:
        GLSL code string for the start command or None if not a valid start command
    """
    start_match = START_PATTERN.match(line)
    if start_match:
        size = int(start_match.group(1))
        pos_x = int(start_match.group(2))
        pos_y = int(start_match.group(3))
        return f'beginTextM({size}, vec2({pos_x}, {pos_y}));'
    return None

def process_color_command(line: str) -> Optional[str]:
    """
    Process vec3() command and return corresponding GLSL code.
    
    Args:
        line: The vec3 color command line
        
    Returns:
        GLSL code string for the color setting or None if not a valid color command
    """
    color_match = COLOR_PATTERN.match(line)
    if color_match:
        r = float(color_match.group(1))
        g = float(color_match.group(2)) if color_match.group(2) else r
        b = float(color_match.group(3)) if color_match.group(3) else r
        return f'    text.fgCol = vec4({r}, {g}, {b}, 1.0);'
    return None

def process_text_line(line: str) -> Union[str, List[str]]:
    """
    Process a text line and return corresponding GLSL code.
    
    Args:
        line: The text line to process
        
    Returns:
        GLSL code string or list of strings for the text line
    """
    if not line:
        return EMPTY_LINE_RESULT
    
    char_identifiers = convert_to_chars(line)
    return [
        f'    printString(({", ".join(char_identifiers)}));',
        EMPTY_LINE_RESULT
    ]

def parse_and_convert(input_text: str) -> str:
    """
    Parse the input text and convert to GLSL format.
    
    Args:
        input_text: The raw input text to convert
        
    Returns:
        Converted GLSL code as a string
        
    Raises:
        ValueError: If the input text has invalid format or structure
    """
    lines = input_text.split('\n')
    validate_text(lines)
    
    output = []
    in_section = False
    
    # Check for darken() at the first line
    if lines and lines[0].strip().startswith('darken('):
        output.append(process_darken_command(lines[0]))
        # Remove the first line as it's been processed
        lines = lines[1:]
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Check for misplaced darken() command
        if line.startswith('darken('):
            raise ValueError(f"darken() command can only be used on the first line, found on line {i+1}")
        
        # Check for start command
        start_result = process_start_command(line)
        if start_result:
            output.append(start_result)
            in_section = True
            i += 1
            continue
        
        # Check for vec3 color command
        color_result = process_color_command(line)
        if color_result and in_section:
            output.append(color_result)
            i += 1
            continue
        
        # End command
        if line == 'end()':
            output.append(SECTION_END_RESULT)
            in_section = False
            i += 1
            continue
        
        # Validate text placement
        if line and not start_result and not color_result:
            if not in_section:
                raise ValueError(f"Text found outside of section boundaries on line {i+1}")
            
            # Process text line
            text_results = process_text_line(line)
            if isinstance(text_results, list):
                output.extend(text_results)
            else:
                output.append(text_results)
        elif not line and in_section:
            # Empty line - add printLine() only within a section
            output.append(EMPTY_LINE_RESULT)
        
        i += 1
    
    # Validate no open sections
    if in_section:
        raise ValueError("Unclosed section: missing end() command")
    
    return '\n'.join(output)

def copy_to_clipboard(text: str) -> bool:
    """
    Copy text to clipboard if pyperclip is available.
    
    Args:
        text: The text to copy to clipboard
        
    Returns:
        True if successfully copied, False otherwise
    """
    if CLIPBOARD_AVAILABLE:
        try:
            pyperclip.copy(text)
            return True
        except Exception:
            return False
    return False

def main() -> None:
    """
    Main function to run the text conversion tool.
    """
    print("\n" + "="*60)
    print("  TEXT TO GLSL CONVERTER FOR COMPLEMENTARY SHADERS")
    print("  by @SpacEagle17")
    print("="*60)
    
    # Ask for file location and remove quotes
    file_path = input("\nEnter the path to the .txt file: ").strip().strip('"\'')
    
    try:
        # Read input file
        with open(file_path, 'r') as file:
            input_text = file.read()
        
        # Convert text
        converted_text = parse_and_convert(input_text)
        
        # Print converted text to console with nice formatting
        print("\n" + "="*60)
        print("CONVERTED TEXT:")
        print("="*60)
        print(converted_text)
        
        # Generate output file path
        base, ext = os.path.splitext(file_path)
        output_path = f"{base}_converted{ext}"
        
        # Write converted text to new file
        with open(output_path, 'w') as file:
            file.write(converted_text)
        
        # Summary
        print("\n" + "="*60)
        print("SUMMARY:")
        print(f"  Input file: {file_path}")
        print(f"  Output file: {output_path}")

        # Try to copy to clipboard if available
        if copy_to_clipboard(converted_text):
            print("  Text copied to clipboard")
        elif CLIPBOARD_AVAILABLE:
            print("  Could not copy to clipboard due to an error")
        else:
            print("  Clipboard functionality not available. Install pyperclip for this feature")

        print(f"  Text length: {len(converted_text)} characters")
        print("="*60)
    
    except FileNotFoundError:
        print("\nERROR: File not found!")
        print(f"Could not find file at: {file_path}")
        print("Please check the path and try again.")
    
    except ValueError as e:
        print("\nERROR: Invalid input format!")
        print(f"{e}")
    
    except Exception as e:
        print("\nERROR: Unexpected error!")
        print(f"{e}")
        print("Please report this issue if it persists.")

if __name__ == '__main__':
    main()
