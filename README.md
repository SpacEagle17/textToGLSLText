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
- Space, ., -, ,, :, _, ", !, >, <, [, ], (, ), =, +


## COMMANDS:
- `start(size, x, y)`: Start a new text section with size and position
- `vec3(r, g, b)`: Set the color for the text section - can be in `vec3(1.0, 1.0, 1.0)` or `vec3(1, 1, 1)` or `vec3(1)` format
- `end()`: End the current text section
