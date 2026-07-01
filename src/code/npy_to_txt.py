import numpy as np
npy_filepath = 'picachu_simplified.npy'
txt_filepath = '1.txt'
newtxt_file_filepath = 'picachu.txt'
data = np.load(npy_filepath)
np.savetxt(txt_filepath, data)
with open(txt_filepath, 'r') as f:
    lines = f.readlines()
merged_lines = ''
for i in range(len(lines)):
    lines[i] = lines[i].rstrip('\n')
for i in range(0, len(lines)):
    merged_lines += lines[i] + '\n'
with open(newtxt_file_filepath, 'w') as f:
    f.write(merged_lines)