import re
import os

# Try to import pyperclip but don't fail if it's not available
try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False

'''
    INSTRUCTIONS:
    by @SpacEagle17

    1. Create a .txt file with the following format (can repeat multiple times)):
    [darken(value)]  # Optional, first line only
    start(size, x, y)
    vec3(r, g, b)
    Text to convert
    end()
    2. Run the script and enter the path to the .txt file when prompted
    3. The converted text will be printed to the console and saved to a new file

    
    EXAMPLE:
    darken(0.5)      # Optional - darkens the background
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


    ALLOWED CHARACTERS:
    - Alphanumeric characters
    - Space, ., -, ,, :, _, ", !, >, <, [, ], (, ), =, +


    COMMANDS:
    - darken(value): Optional, first line only. Darkens the background. Default: 0.65
    - start(size, x, y): Start a new text section with size and position
    - vec3(r, g, b): Set the color for the text section - can be in vec3(1.0, 1.0, 1.0) or vec3(1, 1, 1) or vec3(1) format
    - end(): End the current text section
    
'''

# Special character mapping
SPECIAL_CHARS = {
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
CHAR_TO_SPECIAL = {
    ' ': 'space', '.': 'dot', '-': 'minus', ',': 'comma', 
    ':': 'colon', '_': 'under', '"': 'quote', '!': 'exclm', 
    '>': 'gt', '<': 'lt', '[': 'opsqr', ']': 'clsqr', 
    '(': 'opprn', ')': 'clprn', '█': 'block', '©': 'copyr', 
    '=': 'equal', '+': 'plus'
}

def is_valid_char(char, is_command_line=False):
    """Check if character is allowed."""
    return (char.isalnum() or 
            char in CHAR_TO_SPECIAL or 
            (is_command_line and char in '()'))

def convert_to_chars(text):
    """Convert text to character identifiers."""
    converted_chars = []
    for char in text:
        if char.isupper():
            converted_chars.append(f'_{char}')
        elif char.islower():
            converted_chars.append(f'_{char}')
        elif char in CHAR_TO_SPECIAL:
            converted_chars.append(SPECIAL_CHARS[CHAR_TO_SPECIAL[char]])
        else:
            converted_chars.append(f'_{char}')
    return converted_chars

def validate_text(lines):
    """Validate text for allowed characters."""
    for line_num, line in enumerate(lines, 1):
        # Check if the line is a command line
        is_command_line = (
            line.startswith('start(') or 
            line.startswith('vec3(') or 
            line == 'end()' or
            line.startswith('darken(')  # Add darken command
        )
        
        for char in line:
            if not is_valid_char(char, is_command_line):
                raise ValueError(f"Illegal character '{char}' found on line {line_num}")

def parse_and_convert(input_text):
    """Parse the input text and convert to target format."""
    lines = input_text.split('\n')
    validate_text(lines)
    
    output = []
    current_size = None
    current_pos = None
    in_section = False
    
    # Check for darken() at the first line
    if lines and lines[0].strip().startswith('darken('):
        darken_match = re.match(r'darken\((\d+(?:\.\d+)?)\)', lines[0].strip())
        if darken_match:
            # Extract darkness value if provided
            darkness = float(darken_match.group(1))
            output.append(f'color.rgb = mix(color.rgb, vec3(0.0), {darkness});')
        elif lines[0].strip() == 'darken()':
            # Use default darkness value
            output.append('color.rgb = mix(color.rgb, vec3(0.0), 0.65);')
        else:
            raise ValueError("Invalid darken() format. Use darken() or darken(value)")
        
        # Remove the first line as it's been processed
        lines = lines[1:]
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Check for misplaced darken() command
        if line.startswith('darken('):
            raise ValueError(f"darken() command can only be used on the first line, found on line {i+1}")
        
        # Check for start command
        start_match = re.match(r'start\((\d+),\s*(\d+),\s*(\d+)\)', line)
        if start_match:
            current_size = int(start_match.group(1))
            current_pos = (int(start_match.group(2)), int(start_match.group(3)))
            output.append(f'beginTextM({current_size}, vec2({current_pos[0]}, {current_pos[1]}));')
            in_section = True
            i += 1
            continue
        
        # Check for vec3 color with more flexible parsing
        color_match = re.match(r'vec3\((\d+(?:\.\d+)?)\s*(?:,\s*(\d+(?:\.\d+)?)\s*(?:,\s*(\d+(?:\.\d+)?))?)?\)', line)
        if color_match and in_section:
            # Parse color values with default behavior
            r = float(color_match.group(1))
            g = float(color_match.group(2)) if color_match.group(2) else r
            b = float(color_match.group(3)) if color_match.group(3) else r
            
            output.append(f'    text.fgCol = vec4({r}, {g}, {b}, 1.0);')
            i += 1
            continue
        
        # End command
        if line == 'end()':
            output.append('endText(color.rgb);')
            in_section = False
            i += 1
            continue
        
        # Validate text placement
        if line and not start_match and not color_match:
            if not in_section:
                raise ValueError(f"Text found outside of section boundaries on line {i+1}")
            
            # Convert text to character identifiers
            char_identifiers = convert_to_chars(line)
            output.append(f'    printString(({", ".join(char_identifiers)}));')
            output.append('    printLine();')
        elif not line and in_section:
            # Empty line - add printLine() only within a section
            output.append('    printLine();')
        
        i += 1
    
    # Validate no open sections
    if in_section:
        raise ValueError("Unclosed section: missing end() command")
    
    return '\n'.join(output)

def copy_to_clipboard(text):
    """Copy text to clipboard if pyperclip is available."""
    if CLIPBOARD_AVAILABLE:
        try:
            pyperclip.copy(text)
            return True
        except Exception:
            return False
    return False

def main():
    # Ask for file location and remove quotes
    file_path = input("Enter the path to the .txt file: ").strip().strip('"\'')
    
    try:
        # Read input file
        with open(file_path, 'r') as file:
            input_text = file.read()
        
        # Convert text
        converted_text = parse_and_convert(input_text)
        
        # Print converted text to console
        print("\nConverted Text:")
        print(converted_text)
        
        # Try to copy to clipboard if available
        if copy_to_clipboard(converted_text):
            print("Converted text has been copied to clipboard.")
        elif CLIPBOARD_AVAILABLE:
            print("Could not copy to clipboard due to an error.")
        else:
            print("Clipboard functionality not available. Install pyperclip for this feature.")
        
        # Generate output file path
        base, ext = os.path.splitext(file_path)
        output_path = f"{base}_converted{ext}"
        
        # Write converted text to new file
        with open(output_path, 'w') as file:
            file.write(converted_text)
        
        print(f"\nConverted file saved to: {output_path}")
    
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    main()
