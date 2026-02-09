#!/usr/bin/env python3
"""Fix voice loading in helper.py"""

with open('helper.py', 'r') as f:
    lines = f.readlines()

# Find the section to replace
new_lines = []
i = 0
while i < len(lines):
    if 'expected_size = self.STYLE_DIM' in lines[i] and i < len(lines) - 5:
        # Found the line, skip next 4 lines and add our new code
        new_lines.append('        # Validate size - Supertonic 2 uses 101 style embeddings\n')
        new_lines.append('        expected_size = 101 * self.STYLE_DIM  # 101 * 128 = 12928\n')
        i += 5  # Skip old code
        continue
    elif 'return style_vec.reshape(1, -1, self.STYLE_DIM)' in lines[i]:
        new_lines.append('        return style_vec.reshape(1, 101, self.STYLE_DIM)\n')
    elif 'Style vector as numpy array with shape (1, 1, STYLE_DIM)' in lines[i]:
        new_lines.append('Style vector as numpy array with shape (1, 101, STYLE_DIM)')
    else:
        new_lines.append(lines[i])
    i += 1

with open('helper.py', 'w') as f:
    f.writelines(new_lines)

print("Fixed helper.py")
