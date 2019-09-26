import os
import sys

import numpy as np

in_file = sys.argv[1]

with open(in_file, 'r') as fp1:
    with open(in_file.replace('.TXT', '_new.csv'), 'w') as fp2:
        data = fp1.readline().replace('\t', ',')
        fp2.write(data)
        
        for row in fp1.readlines():
            data = row.replace('\t', ',')
            fp2.write(data)
