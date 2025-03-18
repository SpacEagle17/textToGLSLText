# Text to GLSL
Python script tailored specifically to the SixthSurge's Text Printing Library included in Complementary Shaders and the beginTextM() function

## INSTRUCTIONS:

1. Create a .txt file with the following format (can repeat multiple times)):
```
start(size, x, y)
vec3(r, g, b)
Text to convert
end()
```
3. Run the script and enter the path to the .txt file when prompted
4. The converted text will be printed to the console and saved to a new file


## EXAMPLE:
```
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
```

<details><summary>Click for the output</summary>
<p>

```
color.rgb = mix(color.rgb, vec3(0.0), 0.5);
beginTextM(4, vec2(30, 30));
    text.fgCol = vec4(1.0, 0.0, 0.0, 1.0);
    printString((_B, _I, _G, _space, _T, _I, _T, _L, _E));
    printLine();
endText(color.rgb);
beginTextM(2, vec2(0, 80));
    text.fgCol = vec4(1.0, 1.0, 1.0, 1.0);
    printString((_H, _e, _l, _l, _o, _space, _m, _y, _space, _n, _a, _m, _e, _space, _i, _s, _space, _X, _Y, _Z, _dot));
    printLine();
    printString((_I, _space, _l, _i, _k, _e, _space, _p, _o, _t, _a, _t, _o, _e, _s, _comma, _space, _v, _e, _r, _y, _space, _m, _u, _c, _h, _colon, _space, _o, _k, _exclm));
    printLine();
    printLine();
    text.fgCol = vec4(1.0, 0.0, 0.0, 1.0);
    printString((_A, _A, _A, _A, _A, _A, _A, _A, _A, _A, _A, _A, _A, _A, _A));
    printLine();
    printLine();
    printLine();
    printLine();
    text.fgCol = vec4(1.0, 1.0, 1.0, 1.0);
    printString((_T, _h, _i, _s, _space, _i, _s, _space, _a, _space, _n, _e, _w, _space, _p, _a, _r, _a, _g, _r, _a, _p, _h));
    printLine();
    printString((_dot, _space, _minus, _comma, _colon, _under, _quote, _exclm, _lt, _gt, _opsqr, _clsqr, _opprn, _clprn, _equal, _plus));
    printLine();
    text.fgCol = vec4(1.0, 0.0, 1.0, 1.0);
    printString((_T, _h, _i, _s, _space, _t, _e, _x, _t, _space, _h, _a, _s, _space, _a, _space, _n, _e, _w, _space, _c, _o, _l, _o, _r));
    printLine();
endText(color.rgb);
```
  
</p>
</details>


## ALLOWED CHARACTERS:
- Alphanumeric characters
- Space, ., -, ,, :, _, ", !, >, <, [, ], (, ), =, +, /

`+ and / are Euphoria Patches Exclusive`


## COMMANDS:
- `darken(value)`: Optional, first line only. Darkens the background. Default: 0.65 - Allowed range: 0.0 to 1.0
- `start(size, x, y)`: Start a new text section with size and position
- `vec3(r, g, b)`: Set the color for the text section - can be in `vec3(1.0, 1.0, 1.0)` or `vec3(1, 1, 1)` or `vec3(1)` format
- `end()`: End the current text section

## SHORTCUT COMMANDS:
### They are optional replacements for start()
- `Title([size, [x, y]])`: Quick way to start a title section with default values: size=8, x=6, y=10
- `Text([size, [x, y]])`: Quick way to start a text section with default values: size=4, x=15, y=36
- `Footnote([size, [x, y]])`: Quick way to start a footnote section with default values: size=2, x=30, y=calculated
  Note: `Footnote()` calculates y position based on the previous section when not specified.
        `Y = prev_section_y + (15 * number_of_lines_in_prev_section) + 36`

## SHORTCUT EXAMPLE:
```
darken(0.5)
Title()
This is a title with default settings
end()

Text(5, 10)  
This is regular text with custom size and x position
end()

Footnote()
This footnote will be positioned automatically based on the text above
end()
```
