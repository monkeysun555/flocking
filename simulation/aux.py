import numpy as np
import os 
from config import Config
import random

def static_bw_traces(data_dir = Config.ori_bw_trace_path):
    bw_traces = []
    datas = os.listdir(data_dir)
    for data in datas:
        if 'DS' in data:
            continue
        path = data_dir + data
        bw_trace_name = data.split('_')[3].split('.')[0]
        bw_trace = []
        with open(path) as f:
            # content = f.readlines()
            for line in f.readlines():
                info = line.strip('\n').split()
                bw_trace.append(float(info[1]))
        bw_traces.append([np.std(bw_trace)/np.mean(bw_trace), np.mean(bw_trace), np.std(bw_trace), data.split('_')[3].split('.')[0]])

    bw_traces.sort()
    for bw in bw_traces:
      print(bw)
    traces1 = bw_traces[:20]
    traces2 = bw_traces[40:80]
    traces3 = bw_traces[95:145]
    traces4 = bw_traces[155:175]

    selected_traces = []
    group = []
    for i in range(12):
        j = random.randint(0,len(traces1)-1)
        group.append(traces1[j][3])
        del traces1[j]
    selected_traces.append(group)

    group = []
    for i in range(12):
        j = random.randint(0,len(traces2)-1)
        group.append(traces2[j][3])
        del traces2[j]
    selected_traces.append(group)

    group = []
    for i in range(12):
        j = random.randint(0,len(traces3)-1)
        group.append(traces3[j][3])
        del traces3[j]
    selected_traces.append(group)
    
    group = []
    for i in range(12):
        j = random.randint(0,len(traces4)-1)
        group.append(traces4[j][3])
        del traces4[j]
    selected_traces.append(group)

    print(selected_traces)

def main():
    static_bw_traces()
    # a = load_fovs_for_video()
    # print(a)

if __name__ == '__main__':
    main()