# This for edge ploting 
import caching
import numpy as np
import os 
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42

new_palette = ['#1f77b4',  '#ff7f0e',  '#2ca02c',
                  '#d62728', '#9467bd',
                  '#8c564b', '#e377c2', '#7f7f7f',
                  '#bcbd22', '#17becf']
patterns = [ "/" , "|" , "\\"  , "-" , "+" , "x", "o", "O", ".", "*" ]


# CACHE_METHOD = 7            # 0: cache all, 1: simpe transcoding (high to low) 2.  highest for tile, 3 highest all tiles 
#                             # 4: Limited size, LRU, 5 transcoding, 6: highest rate for tile 
#                             # 7: 8: 9:
# REPRE_METHOD = 1            # 0: REPRE 1: NOT REPRE 2: GLOBAL_NOT, 3 GLOBAL_W_NOT
COOR = 1
OPTIMIZE = 1
RUN_CASE = 3                  # Case 0: unlimited  case 1:limited size, compare cache algo, 2: #tiles curve 3 bits curve 4: limited to 30s and show figure of version 0
REDO_CACHING = 0              # If redo caching and calculate ratios
SIZE = 150                     # Case 1 size: 60 DO NOT CHANGE
size_curve_list = [150, 210, 300, 600, 1200, 2400]
# size_curve_list = [30, 60]
size_bit_curve_list = [5000, 10000, 20000, 30000, 60000, 120000, 180000] # in Mbits [2500, ...., 30000]

def main():
    ratio_path = './cache_ratio_results/'
    if RUN_CASE == 4:
        hitrate_list = []
        bandwidth_saved_ratios = []
        size_list = []
        transcoding_list = []
        current_case_path = ratio_path + 'duration/'
        if not os.path.isdir(current_case_path):
            os.makedirs(current_case_path)
        # Figure 0: Compare unlimited size, hitrate and saved bandwidth
        if REDO_CACHING:
            for method in [16,17,18,19]:
                cache = caching.edge_cache(COOR, OPTIMIZE, method, float('inf'),interval=35)
                cache.load_cache_data()
                current_size, cache_count, n_request_tiles, \
                hitrate, num_bit_total, num_bit_transmitted, n_transcoding, size_in_bit = cache.do_caching()
                hitrate_list.append((method, hitrate))
                bandwidth_saved_ratios.append((method, (num_bit_total- num_bit_transmitted)/num_bit_total))
                size_list.append((method, current_size))
                transcoding_list.append((method, n_transcoding/n_request_tiles))
            print("Case 1, duration ", hitrate_list, bandwidth_saved_ratios)
            
            ratio_write = open(current_case_path + 'coor' + str(COOR) + '_opt' + str(OPTIMIZE) + '.txt', 'w')
            ratio_write.write('Hitrate: ')
            for hr in hitrate_list:
                ratio_write.write(str(hr[1])+' ')
            ratio_write.write('\n')
            ratio_write.write('Band_Ratio: ')
            for br in bandwidth_saved_ratios:
                ratio_write.write(str(br[1])+ ' ')
            ratio_write.write('\n')
            ratio_write.write('Final_Size: ')
            for size in size_list:
                ratio_write.write(str(size[1])+ ' ')
            ratio_write.write('\n')
            ratio_write.write('Transcoding: ')
            for size in transcoding_list:
                ratio_write.write(str(size[1])+ ' ')
            ratio_write.write('\n')
            hitrate_list = [x[1] for x in hitrate_list]
            bandwidth_saved_ratios = [x[1] for x in bandwidth_saved_ratios]
            size_list = [x[1] for x in size_list]
            transcoding_list = [x[1] for x in transcoding_list]
        else:
            # Read
            results_path = ratio_path + 'duration/' + 'coor' + str(COOR) + '_opt' + str(OPTIMIZE) + '.txt'
            with open(results_path, 'r') as results_read:
                for line in results_read:
                    if line.split(' ')[0] == 'Hitrate:':
                        hitrate_list = line.strip('\n').split(' ')[1:-1]
                    elif line.split(' ')[0] == 'Band_Ratio:':
                        bandwidth_saved_ratios = line.strip('\n').split(' ')[1:-1]
                    elif line.split(' ')[0] == 'Final_Size:':
                        size_list = line.strip('\n').split(' ')[1:-1]
                    elif line.split(' ')[0] == 'Transcoding:':
                        transcoding_list = line.strip('\n').split(' ')[1:-1]
                    else:
                        assert 0 == 1
        print(size_list)
        p = plot_bar_unlimited(hitrate_list, bandwidth_saved_ratios, size_list, transcoding_list)
        p.savefig(ratio_path + 'duration/duration_hit_br_coor' + str(COOR) + '_opt' + str(OPTIMIZE) + '.eps', format='eps', dpi=1000, figsize=(9, 7))

        # plot size and transcoding curve
        q = plot_curve_duration()
        q.savefig(ratio_path + 'duration/duration_curve_coor' + str(COOR) + '_opt' + str(OPTIMIZE) + '.eps', format='eps', dpi=1000, figsize=(9, 7))
    
    elif RUN_CASE == 0:
        hitrate_list = []
        bandwidth_saved_ratios = []
        size_list = []
        transcoding_list = []
        # Figure 0: Compare unlimited size, hitrate and saved bandwidth
        if REDO_CACHING:
            for method in [0,1,2,3]:
                cache = caching.edge_cache(COOR, OPTIMIZE, method, float('inf'))
                cache.load_cache_data()
                current_size, cache_count, n_request_tiles, \
                hitrate, num_bit_total, num_bit_transmitted, n_transcoding, size_in_bit = cache.do_caching()

                hitrate_list.append((method, hitrate))
                bandwidth_saved_ratios.append((method, (num_bit_total- num_bit_transmitted)/num_bit_total))
                size_list.append((method, current_size))
                transcoding_list.append((method, n_transcoding/n_request_tiles))
            print("Case 1, unlimited ", hitrate_list, bandwidth_saved_ratios)
            current_case_path = ratio_path + 'unlimited/'
            if not os.path.isdir(current_case_path):
                os.makedirs(current_case_path)

            ratio_write = open(current_case_path + 'coor' + str(COOR) + '_opt' + str(OPTIMIZE) + '.txt', 'w')
            ratio_write.write('Hitrate: ')
            for hr in hitrate_list:
                ratio_write.write(str(hr[1])+' ')
            ratio_write.write('\n')
            ratio_write.write('Band_Ratio: ')
            for br in bandwidth_saved_ratios:
                ratio_write.write(str(br[1])+ ' ')
            ratio_write.write('\n')
            ratio_write.write('Final_Size: ')
            for size in size_list:
                ratio_write.write(str(size[1])+ ' ')
            ratio_write.write('\n')
            ratio_write.write('Transcoding: ')
            for size in transcoding_list:
                ratio_write.write(str(size[1])+ ' ')
            ratio_write.write('\n')
            hitrate_list = [x[1] for x in hitrate_list]
            bandwidth_saved_ratios = [x[1] for x in bandwidth_saved_ratios]
            size_list = [x[1] for x in size_list]
            transcoding_list = [x[1] for x in transcoding_list]
        else:
            # Read
            results_path = ratio_path + 'unlimited/' + 'coor' + str(COOR) + '_opt' + str(OPTIMIZE) + '.txt'
            with open(results_path, 'r') as results_read:
                for line in results_read:
                    if line.split(' ')[0] == 'Hitrate:':
                        hitrate_list = line.strip('\n').split(' ')[1:-1]
                    elif line.split(' ')[0] == 'Band_Ratio:':
                        bandwidth_saved_ratios = line.strip('\n').split(' ')[1:-1]
                    elif line.split(' ')[0] == 'Final_Size:':
                        size_list = line.strip('\n').split(' ')[1:-1]
                    elif line.split(' ')[0] == 'Transcoding:':
                        transcoding_list = line.strip('\n').split(' ')[1:-1]
                    else:
                        assert 0 == 1
        print(size_list)
        p = plot_bar_unlimited(hitrate_list, bandwidth_saved_ratios, size_list, transcoding_list)
        p.savefig(ratio_path + 'unlimited/unlimit_hit_br_coor' + str(COOR) + '_opt' + str(OPTIMIZE) + '.eps', format='eps', dpi=1000, figsize=(9, 7))

        # plot size and transcoding curve
        q = plot_curve_unlimited()
        q.savefig(ratio_path + 'unlimited/unlimit_curve_coor' + str(COOR) + '_opt' + str(OPTIMIZE) + '.eps', format='eps', dpi=1000, figsize=(9, 7))
    
    elif RUN_CASE == 1:
        hitrate_list = []
        bandwidth_saved_ratios = []
        size_list = []
        new_hitrate_list = []
        new_bandwidth_saved_ratios = []
        new_size_list = []
        # Figure 0: Compare unlimited size, hitrate and saved bandwidth
        if REDO_CACHING:
            for method in [4,7,5,8,6,9]:
                cache = caching.edge_cache(COOR, OPTIMIZE, method, SIZE)
                cache.load_cache_data()
                current_size, cache_count, n_request_tiles, \
                hitrate, num_bit_total, num_bit_transmitted, n_transcoding, size_in_bit = cache.do_caching()

                if method <= 6:
                    hitrate_list.append((method, hitrate))
                    bandwidth_saved_ratios.append((method, (num_bit_total- num_bit_transmitted)/num_bit_total))
                    size_list.append((method, current_size))
                else:
                    new_hitrate_list.append((method, hitrate))
                    new_bandwidth_saved_ratios.append((method, (num_bit_total- num_bit_transmitted)/num_bit_total))
                    new_size_list.append((method, current_size))

            print("Case 2, limited: ", SIZE, hitrate_list, bandwidth_saved_ratios, size_list)
            print("Case 2, limited: ", SIZE, new_hitrate_list, new_bandwidth_saved_ratios, new_size_list)
            current_case_path = ratio_path + 'limited_' + str(SIZE) + '/'
            if not os.path.isdir(current_case_path):
                os.makedirs(current_case_path)
            ratio_write = open(current_case_path + 'coor' + str(COOR) + '_opt' + str(OPTIMIZE) + '.txt', 'w')
            ratio_write.write('Hitrate: ')
            for hr in hitrate_list:
                ratio_write.write(str(hr[1])+' ')
            ratio_write.write('\n')
            ratio_write.write('Band_Ratio: ')
            for br in bandwidth_saved_ratios:
                ratio_write.write(str(br[1])+ ' ')
            ratio_write.write('\n')
            ratio_write.write('Final_Size: ')
            for size in size_list:
                ratio_write.write(str(size[1])+ ' ')
            ratio_write.write('\n')
            ratio_write.write('New_Hitrate: ')
            for hr in new_hitrate_list:
                ratio_write.write(str(hr[1])+' ')
            ratio_write.write('\n')
            ratio_write.write('New_Band_Ratio: ')
            for br in new_bandwidth_saved_ratios:
                ratio_write.write(str(br[1])+ ' ')
            ratio_write.write('\n')
            ratio_write.write('New_Final_Size: ')
            for size in new_size_list:
                ratio_write.write(str(size[1])+ ' ')
            ratio_write.write('\n')
            
            hitrate_list = [x[1] for x in hitrate_list]
            bandwidth_saved_ratios = [x[1] for x in bandwidth_saved_ratios]
            size_list = [x[1] for x in size_list]
            new_hitrate_list = [x[1] for x in new_hitrate_list]
            new_bandwidth_saved_ratios = [x[1] for x in new_bandwidth_saved_ratios]
            new_size_list = [x[1] for x in new_size_list]

        else:
            # Read
            results_path = ratio_path + 'limited_' + str(SIZE) + '/' + 'coor' + str(COOR) + '_opt' + str(OPTIMIZE) + '.txt'
            with open(results_path, 'r') as results_read:
                for line in results_read:
                    if line.split(' ')[0] == 'Hitrate:':
                        hitrate_list = line.strip('\n').split(' ')[1:-1]
                    elif line.split(' ')[0] == 'Band_Ratio:':
                        bandwidth_saved_ratios = line.strip('\n').split(' ')[1:-1]
                    elif line.split(' ')[0] == 'Final_Size:':
                        size_list = line.strip('\n').split(' ')[1:-1]
                    elif line.split(' ')[0] == 'New_Hitrate:':
                        new_hitrate_list = line.strip('\n').split(' ')[1:-1]
                    elif line.split(' ')[0] == 'New_Band_Ratio:':
                        new_bandwidth_saved_ratios = line.strip('\n').split(' ')[1:-1]
                    elif line.split(' ')[0] == 'New_Final_Size:':
                        new_size_list = line.strip('\n').split(' ')[1:-1]
                    else:
                        assert 0 == 1
        print(size_list)
        
        p = plot_bar_limit(hitrate_list, bandwidth_saved_ratios, size_list, new_hitrate_list, new_bandwidth_saved_ratios, new_size_list)
        p.savefig(ratio_path + 'limited_' + str(SIZE) + '/limit_' + str(SIZE) + '_hit_br_coor' + str(COOR) + '_opt' + str(OPTIMIZE) + '.eps', format='eps', dpi=1000, figsize=(11, 7))
        
        # p, q = plot_bar_limit_two_figs(hitrate_list, bandwidth_saved_ratios, size_list, new_hitrate_list, new_bandwidth_saved_ratios, new_size_list)
        # p.savefig(ratio_path + 'limited_' + str(SIZE) + '/limit_60_hit.eps', format='eps', dpi=1000, figsize=(9, 7))
        # q.savefig(ratio_path + 'limited_' + str(SIZE) + '/limit_60_bandwdith.eps', format='eps', dpi=1000, figsize=(9, 7))
    elif RUN_CASE == 2:
        lru_hitrate = []
        lru_trans = []
        lru_trans_enhance = []
        lf_hitrate = []
        lf_trans = []
        lf_trans_enhance = []

        lru_eff = []
        lru_trans_eff = []
        lru_trans_enhance_eff = []
        lf_eff = []
        lf_trans_eff = []
        lf_trans_enhance_eff = []

        # Figure 0: Compare unlimited size, hitrate and saved bandwidth
        if REDO_CACHING:
            for cache_size in size_curve_list:
                for method in [4,5,6,7,8,9]:
                    cache = caching.edge_cache(COOR, OPTIMIZE, method, cache_size)
                    cache.load_cache_data()
                    current_size, cache_count, n_request_tiles, \
                    hitrate, num_bit_total, num_bit_transmitted, n_transcoding, size_in_bit  = cache.do_caching()

                    if method == 4:
                        lru_hitrate.append(hitrate)
                        lru_eff.append((num_bit_total- num_bit_transmitted)/num_bit_total)
                    elif method == 5:
                        lru_trans.append(hitrate)
                        lru_trans_eff.append((num_bit_total- num_bit_transmitted)/num_bit_total)
                    elif method == 6:
                        lru_trans_enhance.append(hitrate)
                        lru_trans_enhance_eff.append((num_bit_total- num_bit_transmitted)/num_bit_total)
                    elif method == 7:
                        lf_hitrate.append(hitrate)
                        lf_eff.append((num_bit_total- num_bit_transmitted)/num_bit_total)
                    elif method == 8:
                        lf_trans.append(hitrate)
                        lf_trans_eff.append((num_bit_total- num_bit_transmitted)/num_bit_total)
                    elif method == 9:
                        lf_trans_enhance.append(hitrate)
                        lf_trans_enhance_eff.append((num_bit_total- num_bit_transmitted)/num_bit_total)
            
            current_case_path = ratio_path + 'size_curve/'
            if not os.path.isdir(current_case_path):
                os.makedirs(current_case_path)
            ratio_write = open(current_case_path + 'hit_coor' + str(COOR) + '_opt' + str(OPTIMIZE) + '.txt', 'w')
            ratio_write.write('LRU: ')
            for hr in lru_hitrate:
                ratio_write.write(str(hr)+' ')
            ratio_write.write('\n')

            ratio_write.write('LRU_Trans: ')
            for br in lru_trans:
                ratio_write.write(str(br)+ ' ')
            ratio_write.write('\n')

            ratio_write.write('LRU_Trans_Enhance: ')
            for size in lru_trans_enhance:
                ratio_write.write(str(size)+ ' ')
            ratio_write.write('\n')

            ratio_write.write('LF: ')
            for hr in lf_hitrate:
                ratio_write.write(str(hr)+' ')
            ratio_write.write('\n')

            ratio_write.write('LF_Trans: ')
            for br in lf_trans:
                ratio_write.write(str(br)+ ' ')
            ratio_write.write('\n')

            ratio_write.write('LF_Trans_Enhance: ')
            for size in lf_trans_enhance:
                ratio_write.write(str(size)+ ' ')
            ratio_write.write('\n')

            br_write = open(current_case_path + 'br_coor' + str(COOR) + '_opt' + str(OPTIMIZE) + '.txt', 'w')
            br_write.write('LRU: ')
            for hr in lru_eff:
                br_write.write(str(hr)+' ')
            br_write.write('\n')

            br_write.write('LRU_Trans: ')
            for br in lru_trans_eff:
                br_write.write(str(br)+ ' ')
            br_write.write('\n')

            br_write.write('LRU_Trans_Enhance: ')
            for size in lru_trans_enhance_eff:
                br_write.write(str(size)+ ' ')
            br_write.write('\n')

            br_write.write('LF: ')
            for hr in lf_eff:
                br_write.write(str(hr)+' ')
            br_write.write('\n')

            br_write.write('LF_Trans: ')
            for br in lf_trans_eff:
                br_write.write(str(br)+ ' ')
            br_write.write('\n')

            br_write.write('LF_Trans_Enhance: ')
            for size in lf_trans_enhance_eff:
                br_write.write(str(size)+ ' ')
            br_write.write('\n')
        else:
            # Read
            results_path = ratio_path + 'size_curve/' + 'hit_coor' + str(COOR) + '_opt' + str(OPTIMIZE) + '.txt'
            with open(results_path, 'r') as results_read:
                for line in results_read:
                    if line.split(' ')[0] == 'LRU:':
                        lru_hitrate = line.strip('\n').split(' ')[1:-1]
                    elif line.split(' ')[0] == 'LRU_Trans:':
                        lru_trans = line.strip('\n').split(' ')[1:-1]
                    elif line.split(' ')[0] == 'LRU_Trans_Enhance:':
                        lru_trans_enhance = line.strip('\n').split(' ')[1:-1]
                    elif line.split(' ')[0] == 'LF:':
                        lf_hitrate = line.strip('\n').split(' ')[1:-1]
                    elif line.split(' ')[0] == 'LF_Trans:':
                        lf_trans = line.strip('\n').split(' ')[1:-1]
                    elif line.split(' ')[0] == 'LF_Trans_Enhance:':
                        lf_trans_enhance = line.strip('\n').split(' ')[1:-1]
                    else:
                        assert 0 == 1

            results_path = ratio_path + 'size_curve/' + 'br_coor' + str(COOR) + '_opt' + str(OPTIMIZE) + '.txt'
            with open(results_path, 'r') as results_read:
                for line in results_read:
                    if line.split(' ')[0] == 'LRU:':
                        lru_eff = line.strip('\n').split(' ')[1:-1]
                    elif line.split(' ')[0] == 'LRU_Trans:':
                        lru_trans_eff = line.strip('\n').split(' ')[1:-1]
                    elif line.split(' ')[0] == 'LRU_Trans_Enhance:':
                        lru_trans_enhance_eff = line.strip('\n').split(' ')[1:-1]
                    elif line.split(' ')[0] == 'LF:':
                        lf_eff = line.strip('\n').split(' ')[1:-1]
                    elif line.split(' ')[0] == 'LF_Trans:':
                        lf_trans_eff = line.strip('\n').split(' ')[1:-1]
                    elif line.split(' ')[0] == 'LF_Trans_Enhance:':
                        lf_trans_enhance_eff = line.strip('\n').split(' ')[1:-1]
                    else:
                        assert 0 == 1

        p,q = plot_size_curve([lru_hitrate,  lru_trans, lru_trans_enhance, lf_hitrate, lf_trans, lf_trans_enhance],\
                            [lru_eff, lru_trans_eff, lru_trans_enhance_eff, lf_eff, lf_trans_eff, lf_trans_enhance_eff])
        p.savefig(ratio_path + 'size_curve/curve_hitrate_coor' + str(COOR) + '_opt' + str(OPTIMIZE) + '.eps', format='eps', dpi=1000, figsize=(9, 7))
        q.savefig(ratio_path + 'size_curve/curve_br_coor' + str(COOR) + '_opt' + str(OPTIMIZE) + '.eps', format='eps', dpi=1000, figsize=(9, 7))

        
    elif RUN_CASE == 3:
        lru_hitrate = []
        lru_trans = []
        lru_trans_enhance = []
        lf_hitrate = []
        lf_trans = []
        lf_trans_enhance = []

        lru_eff = []
        lru_trans_eff = []
        lru_trans_enhance_eff = []
        lf_eff = []
        lf_trans_eff = []
        lf_trans_enhance_eff = []

        # Figure 0: Compare unlimited size, hitrate and saved bandwidth
        if REDO_CACHING:
            for cache_size in size_bit_curve_list:
                for method in [10, 11, 12, 13, 14, 15]:
                    cache = caching.edge_cache(COOR, OPTIMIZE, method, cache_size)
                    cache.load_cache_data()
                    current_size, cache_count, n_request_tiles, \
                    hitrate, num_bit_total, num_bit_transmitted, n_transcoding, size_in_bit = cache.do_caching()

                    if method == 10:
                        lru_hitrate.append(hitrate)
                        lru_eff.append((num_bit_total- num_bit_transmitted)/num_bit_total)
                    elif method == 11:
                        lru_trans.append(hitrate)
                        lru_trans_eff.append((num_bit_total- num_bit_transmitted)/num_bit_total)
                    elif method == 12:
                        lru_trans_enhance.append(hitrate)
                        lru_trans_enhance_eff.append((num_bit_total- num_bit_transmitted)/num_bit_total)
                    elif method == 13:
                        lf_hitrate.append(hitrate)
                        lf_eff.append((num_bit_total- num_bit_transmitted)/num_bit_total)
                    elif method == 14:
                        lf_trans.append(hitrate)
                        lf_trans_eff.append((num_bit_total- num_bit_transmitted)/num_bit_total)
                    elif method == 15:
                        lf_trans_enhance.append(hitrate)
                        lf_trans_enhance_eff.append((num_bit_total- num_bit_transmitted)/num_bit_total)
            
            current_case_path = ratio_path + 'size_bit_curve/'
            if not os.path.isdir(current_case_path):
                os.makedirs(current_case_path)
            ratio_write = open(current_case_path + 'hit_coor' + str(COOR) + '_opt' + str(OPTIMIZE) + '.txt', 'w')
            ratio_write.write('LRU: ')
            for hr in lru_hitrate:
                ratio_write.write(str(hr)+' ')
            ratio_write.write('\n')

            ratio_write.write('LRU_Trans: ')
            for br in lru_trans:
                ratio_write.write(str(br)+ ' ')
            ratio_write.write('\n')

            ratio_write.write('LRU_Trans_Enhance: ')
            for size in lru_trans_enhance:
                ratio_write.write(str(size)+ ' ')
            ratio_write.write('\n')

            ratio_write.write('LF: ')
            for hr in lf_hitrate:
                ratio_write.write(str(hr)+' ')
            ratio_write.write('\n')

            ratio_write.write('LF_Trans: ')
            for br in lf_trans:
                ratio_write.write(str(br)+ ' ')
            ratio_write.write('\n')

            ratio_write.write('LF_Trans_Enhance: ')
            for size in lf_trans_enhance:
                ratio_write.write(str(size)+ ' ')
            ratio_write.write('\n')

            br_write = open(current_case_path + 'br_coor' + str(COOR) + '_opt' + str(OPTIMIZE) + '.txt', 'w')
            br_write.write('LRU: ')
            for hr in lru_eff:
                br_write.write(str(hr)+' ')
            br_write.write('\n')

            br_write.write('LRU_Trans: ')
            for br in lru_trans_eff:
                br_write.write(str(br)+ ' ')
            br_write.write('\n')

            br_write.write('LRU_Trans_Enhance: ')
            for size in lru_trans_enhance_eff:
                br_write.write(str(size)+ ' ')
            br_write.write('\n')

            br_write.write('LF: ')
            for hr in lf_eff:
                br_write.write(str(hr)+' ')
            br_write.write('\n')

            br_write.write('LF_Trans: ')
            for br in lf_trans_eff:
                br_write.write(str(br)+ ' ')
            br_write.write('\n')

            br_write.write('LF_Trans_Enhance: ')
            for size in lf_trans_enhance_eff:
                br_write.write(str(size)+ ' ')
            br_write.write('\n')
        else:
            # Read
            results_path = ratio_path + 'size_bit_curve/' + 'hit_coor' + str(COOR) + '_opt' + str(OPTIMIZE) + '.txt'
            with open(results_path, 'r') as results_read:
                for line in results_read:
                    if line.split(' ')[0] == 'LRU:':
                        lru_hitrate = line.strip('\n').split(' ')[1:-1]
                    elif line.split(' ')[0] == 'LRU_Trans:':
                        lru_trans = line.strip('\n').split(' ')[1:-1]
                    elif line.split(' ')[0] == 'LRU_Trans_Enhance:':
                        lru_trans_enhance = line.strip('\n').split(' ')[1:-1]
                    elif line.split(' ')[0] == 'LF:':
                        lf_hitrate = line.strip('\n').split(' ')[1:-1]
                    elif line.split(' ')[0] == 'LF_Trans:':
                        lf_trans = line.strip('\n').split(' ')[1:-1]
                    elif line.split(' ')[0] == 'LF_Trans_Enhance:':
                        lf_trans_enhance = line.strip('\n').split(' ')[1:-1]
                    else:
                        assert 0 == 1

            results_path = ratio_path + 'size_bit_curve/' + 'br_coor' + str(COOR) + '_opt' + str(OPTIMIZE) + '.txt'
            with open(results_path, 'r') as results_read:
                for line in results_read:
                    if line.split(' ')[0] == 'LRU:':
                        lru_eff = line.strip('\n').split(' ')[1:-1]
                    elif line.split(' ')[0] == 'LRU_Trans:':
                        lru_trans_eff = line.strip('\n').split(' ')[1:-1]
                    elif line.split(' ')[0] == 'LRU_Trans_Enhance:':
                        lru_trans_enhance_eff = line.strip('\n').split(' ')[1:-1]
                    elif line.split(' ')[0] == 'LF:':
                        lf_eff = line.strip('\n').split(' ')[1:-1]
                    elif line.split(' ')[0] == 'LF_Trans:':
                        lf_trans_eff = line.strip('\n').split(' ')[1:-1]
                    elif line.split(' ')[0] == 'LF_Trans_Enhance:':
                        lf_trans_enhance_eff = line.strip('\n').split(' ')[1:-1]
                    else:
                        assert 0 == 1

        p,q = plot_size_curve_bit([lru_hitrate,  lru_trans, lru_trans_enhance, lf_hitrate, lf_trans, lf_trans_enhance],\
                            [lru_eff, lru_trans_eff, lru_trans_enhance_eff, lf_eff, lf_trans_eff, lf_trans_enhance_eff])
        p.savefig(ratio_path + 'size_bit_curve/bit_curve_hitrate_coor' + str(COOR) + '_opt' + str(OPTIMIZE) + '.eps', format='eps', dpi=1000, figsize=(9, 7))
        q.savefig(ratio_path + 'size_bit_curve/bit_curve_br_coor' + str(COOR) + '_opt' + str(OPTIMIZE) + '.eps', format='eps', dpi=1000, figsize=(9, 7))

        p,q = plot_size_curve_bit_ppt([lru_hitrate,  lru_trans, lru_trans_enhance, lf_hitrate, lf_trans, lf_trans_enhance],\
                            [lru_eff, lru_trans_eff, lru_trans_enhance_eff, lf_eff, lf_trans_eff, lf_trans_enhance_eff])
        p.savefig(ratio_path + 'size_bit_curve_ppt/bit_curve_hitrate_coor' + str(COOR) + '_opt' + str(OPTIMIZE) + '.eps', format='eps', dpi=1000, figsize=(9, 7))
        q.savefig(ratio_path + 'size_bit_curve_ppt/bit_curve_br_coor' + str(COOR) + '_opt' + str(OPTIMIZE) + '.eps', format='eps', dpi=1000, figsize=(9, 7))


def plot_size_curve_bit_ppt(curves1, curves2):
    labels = ['Naive', 'Transcoding', 'E-Transcoding']
    line_type = ['--', '-']
    markers = ['o', 's']
    p = plt.figure(figsize=(9, 7))
    for i in range(3):
        plt.plot(range(1,len(size_bit_curve_list)+1), [float(x) for x in curves1[i]], color=new_palette[i%3], linewidth=2.0, linestyle=line_type[int(i/3)+1],\
                marker=markers[int(i/3)], markersize=5.0, markeredgewidth=0, label=labels[i])
    plt.plot([0,10], [1,1], '--', linewidth=1.5, color='k')
    y_axis_upper = float(max(curves1[-1]))*1.3
    y_axis_lower = float(min(curves1[0]))*0.9
    plt.xticks(range(1, len(size_bit_curve_list)+1), [str(x/8000.0) for x in size_bit_curve_list], fontsize=20)
    plt.yticks(np.arange(int(y_axis_lower/0.1)*0.1, 1.01, 0.2), fontsize=20)
    plt.axis([1, len(size_bit_curve_list), y_axis_lower, y_axis_upper])
    plt.ylabel('Cachi Hitrate', fontsize=20)
    plt.xlabel('Cache Size (GB)', fontsize=20)
    plt.legend(loc='upper left', fontsize=20, ncol=1)
    plt.subplots_adjust(top=0.99, right=0.95, bottom=0.15, left=0.15)
    plt.close()

    q = plt.figure(figsize=(9.5, 7))
    for i in range(3):
        plt.plot(range(1,len(size_bit_curve_list)+1), [float(x) for x in curves2[i]], color=new_palette[i%3], linewidth=2.0, linestyle=line_type[int(i/3)+1],\
                marker=markers[int(i/3)], markersize=5.0, markeredgewidth=0, label=labels[i])
    plt.plot([0,10], [1,1], '--', linewidth=1.5, color='k')
    y_axis_upper = float(max(curves2[-1]))*1.3
    y_axis_lower = float(curves2[-1][0])*1.2
    plt.xticks(range(1, len(size_bit_curve_list)+1), [str(x/8000.0) for x in size_bit_curve_list], fontsize=20)
    plt.yticks(np.arange(-1.4, 1.01, 0.4), [str(float(x)/10) for x in range(-14, 12, 4)], fontsize=20)
    plt.axis([1, len(size_bit_curve_list), y_axis_lower, y_axis_upper])
    plt.ylabel('Network Efficiency', fontsize=20)
    plt.xlabel('Cache Size (GB)', fontsize=20)
    plt.legend(loc='lower right', fontsize=20, ncol=1)
    plt.subplots_adjust(top=0.99, right=0.95, bottom=0.15, left=0.15)
    plt.close()
    return p, q

def plot_size_curve(curves1, curves2):
    labels = ['LRU Naive', 'LRU Transcoding', 'LRU E-Transcoding', \
                 'LF Naive',  'LF Transcoding','LF E-Transcoding']
    line_type = ['--', '-']
    markers = ['o', 's']
    p = plt.figure(figsize=(9, 7))
    for i in range(len(curves1)):
        plt.plot(range(1,len(size_curve_list)+1), curves1[i], color=new_palette[i%3], linewidth=2.0, linestyle=line_type[int(i/3)],\
                marker=markers[int(i/3)], markersize=5.0, markeredgewidth=0, label=labels[i])
    plt.plot([0,10], [1,1], '--', linewidth=1.5, color='k')
    y_axis_upper = float(max(curves1[-1]))*1.1
    y_axis_lower = float(min(curves1[0]))*0.9
    plt.xticks(range(1, len(size_curve_list)+1), [str(x) for x in size_curve_list], fontsize=20)
    plt.yticks(np.arange(int(y_axis_lower/0.1)*0.1, y_axis_upper, 0.2), fontsize=20)
    plt.axis([1, len(size_curve_list), y_axis_lower, y_axis_upper])
    plt.ylabel('Cache Hitrate', fontsize=20)
    plt.xlabel('Cache Size', fontsize=20)
    plt.legend(loc='upper left', fontsize=20, ncol=1)
    plt.close()

    q = plt.figure(figsize=(9, 7))
    for i in range(len(curves2)):
        plt.plot(range(1,len(size_curve_list)+1), curves2[i], color=new_palette[i%3], linewidth=2.0, linestyle=line_type[int(i/3)],\
                marker=markers[int(i/3)], markersize=5.0, markeredgewidth=0, label=labels[i])
    plt.plot([0,10], [1,1], '--', linewidth=1.5, color='k')
    y_axis_upper = float(max(curves2[-1]))*1.3
    y_axis_lower = float(curves2[-1][0])*1.1
    plt.xticks(range(1, len(size_curve_list)+1), [str(x) for x in size_curve_list], fontsize=20)
    plt.yticks(np.arange(int(y_axis_lower/0.1)*0.1, y_axis_upper, 0.3), fontsize=20)
    plt.axis([1, len(size_curve_list), y_axis_lower, y_axis_upper])
    plt.ylabel('Network Efficiency', fontsize=20)
    plt.xlabel('Cache Size', fontsize=20)
    plt.legend(loc='lower right', fontsize=20, ncol=1)
    plt.close()
    return p, q

def plot_size_curve_bit(curves1, curves2):
    labels = ['LRU Naive', 'LRU Transcoding', 'LRU E-Transcoding', \
                 'LF Naive',  'LF Transcoding','LF E-Transcoding']
    line_type = ['--', '-']
    markers = ['o', 's']
    p = plt.figure(figsize=(9, 7))
    for i in range(len(curves1)):
        plt.plot(range(1,len(size_bit_curve_list)+1), [float(x) for x in curves1[i]], color=new_palette[i%3], linewidth=2.0, linestyle=line_type[int(i/3)],\
                marker=markers[int(i/3)], markersize=5.0, markeredgewidth=0, label=labels[i])
    plt.plot([0,10], [1,1], '--', linewidth=1.5, color='k')
    y_axis_upper = float(max(curves1[-1]))*1.3
    y_axis_lower = float(min(curves1[0]))*0.9
    plt.xticks(range(1, len(size_bit_curve_list)+1), [str(x/8000.0) for x in size_bit_curve_list], fontsize=20)
    plt.yticks(np.arange(int(y_axis_lower/0.1)*0.1, 1.01, 0.2), fontsize=20)
    plt.axis([1, len(size_bit_curve_list), y_axis_lower, y_axis_upper])
    plt.ylabel('Cachi Hitrate', fontsize=20)
    plt.xlabel('Cache Size (GB)', fontsize=20)
    plt.legend(loc='upper left', fontsize=20, ncol=1)
    plt.subplots_adjust(top=0.99, right=0.95, bottom=0.15, left=0.15)
    plt.close()

    q = plt.figure(figsize=(9.5, 7))
    for i in range(len(curves2)):
        plt.plot(range(1,len(size_bit_curve_list)+1), [float(x) for x in curves2[i]], color=new_palette[i%3], linewidth=2.0, linestyle=line_type[int(i/3)],\
                marker=markers[int(i/3)], markersize=5.0, markeredgewidth=0, label=labels[i])
    plt.plot([0,10], [1,1], '--', linewidth=1.5, color='k')
    y_axis_upper = float(max(curves2[-1]))*1.3
    y_axis_lower = float(curves2[-1][0])*1.2
    plt.xticks(range(1, len(size_bit_curve_list)+1), [str(x/8000.0) for x in size_bit_curve_list], fontsize=20)
    plt.yticks(np.arange(-1.4, 1.01, 0.4), [str(float(x)/10) for x in range(-14, 12, 4)], fontsize=20)
    plt.axis([1, len(size_bit_curve_list), y_axis_lower, y_axis_upper])
    plt.ylabel('Network Efficiency', fontsize=20)
    plt.xlabel('Cache Size (GB)', fontsize=20)
    plt.legend(loc='lower right', fontsize=20, ncol=1)
    plt.subplots_adjust(top=0.99, right=0.95, bottom=0.15, left=0.15)
    plt.close()
    return p, q


def plot_bar_limit_two_figs(hitrate_list, bandwidth_saved_ratios, size_list, new_hitrate_list, new_bandwidth_saved_ratios, new_size_list):
    hitrates = [float(x) for x in hitrate_list]
    bandwidth_saved_ratios = [float(x) for x in bandwidth_saved_ratios]
    size_list = [int(x) for x in size_list]
    new_hitrates = [float(x) for x in new_hitrate_list]
    new_bandwidth_saved_ratios = [float(x) for x in new_bandwidth_saved_ratios]
    new_size_list = [int(x) for x in new_size_list]
    y_axis_upper = min(max(new_hitrates)*2.0, 1.0)
    y_axis_lower = min(new_bandwidth_saved_ratios)*1.2

    width = 0.08  # the width of the bars
    pos_gap = 0.016

    position = []
    curr_pos = 0
    for u_id in range(len(hitrates)):
        position.append(curr_pos)
        curr_pos += pos_gap + 2* width + 4*pos_gap

    # Figure 1: hit rate
    p = plt.figure(figsize=(9, 7))
    plt.bar(position, hitrates, color='none', width=width, edgecolor=new_palette[2], \
                hatch=patterns[0]*6, linewidth=1.0, zorder = 0, label='LRU Hit Rate')
    plt.bar(position, hitrates, color='none', width=width, edgecolor='k', linewidth=0.5)
    plt.bar([x + pos_gap + width for x in position], new_hitrates, color='none', width=width, edgecolor=new_palette[3], \
                hatch=patterns[2]*6, linewidth=1.0, zorder = 0, label='LRU Network Efficiency')
    plt.bar([x + pos_gap + width for x in position], new_hitrates, color='none', width=width, edgecolor='k', linewidth=0.5)
    xticks_pos = [position[group_id]+ width+ 0.5*pos_gap for group_id in range(len(hitrates))]
    plt.xticks(xticks_pos, ['Naive Cache', 'Edge \n Transcoding', 'Enhanced Edge \n Transcoding'], fontsize=20)
    plt.yticks(np.arange(int(y_axis_lower/0.1)*0.1, 0.21, 0.1), fontsize=20)
    plt.axis([-0.5*width, position[-1]+ pos_gap + 2*width + 0.5*width, y_axis_lower, y_axis_upper])
    plt.ylabel('Ratio', fontsize=20)

    plt.legend(loc='upper left', fontsize=20, ncol=2)
    plt.close()

    # Figure 2: bandwidth save
    q = plt.figure(figsize=(9, 7))
    plt.bar(position, bandwidth_saved_ratios, color='none', width=width, edgecolor=new_palette[4], \
                hatch=patterns[0]*6, linewidth=1.0, zorder = 0, label='Hit Rate')
    plt.bar(position, bandwidth_saved_ratios, color='none', width=width, edgecolor='k', linewidth=0.5)
    plt.bar([x + pos_gap + width for x in position], new_bandwidth_saved_ratios, color='none', width=width, edgecolor=new_palette[5], \
                hatch=patterns[2]*6, linewidth=1.0, zorder = 0, label='Traffic Efficiency Ratio')
    plt.bar([x + pos_gap + width for x in position], new_bandwidth_saved_ratios, color='none', width=width, edgecolor='k', linewidth=0.5)   
    plt.plot([-1, 4], [0, 0], color='k', linewidth=1)
    xticks_pos = [position[group_id]+width+0.5*pos_gap for group_id in range(len(hitrates))]
    plt.xticks(xticks_pos, ['Naive Cache', 'Edge \n Transcoding', 'Enhanced Edge \n Transcoding'], fontsize=20)
    plt.yticks(np.arange(0, y_axis_upper, 0.05), fontsize=20)
    plt.axis([-0.5*width, position[-1]+ pos_gap + 2.5*width, min(bandwidth_saved_ratios), y_axis_upper])
    plt.ylabel('Ratio', fontsize=20)

    plt.legend(loc='upper right', fontsize=20, ncol=2)
    plt.close()

    return p,q


def plot_bar_limit(hitrate_list, bandwidth_saved_ratios, size_list, new_hitrate_list, new_bandwidth_saved_ratios, new_size_list):
    hitrates = [float(x) for x in hitrate_list]
    bandwidth_saved_ratios = [float(x) for x in bandwidth_saved_ratios]
    size_list = [int(x) for x in size_list]
    new_hitrates = [float(x) for x in new_hitrate_list]
    new_bandwidth_saved_ratios = [float(x) for x in new_bandwidth_saved_ratios]
    new_size_list = [int(x) for x in new_size_list]
    y_axis_upper = max(new_hitrates)*2.0
    y_axis_lower = min(new_bandwidth_saved_ratios)
    print(y_axis_lower)

    width = 0.08  # the width of the bars
    pos_gap = 0.016

    position = []
    curr_pos = 0
    for u_id in range(len(hitrates)):
        position.append(curr_pos)
        curr_pos += 5*pos_gap + 4* width + 8*pos_gap

    # Figure 1: hit rate
    
    f, (ax, ax2) = plt.subplots(2, 1, sharex=True, figsize=(11,7))
    out = f.add_subplot(111, frameon=False)
    # hide tick and tick label of the big axes
    out.spines['top'].set_color('none')
    out.spines['bottom'].set_color('none')
    out.spines['left'].set_color('none')
    out.spines['right'].set_color('none')
    out.set_xticks([])
    out.set_yticks([0])
    out.set_yticklabels(['1'], fontsize=24, color='w')

    out.set_ylabel("Ratio", fontsize=20)

    ax.bar(position, hitrates, color='none', width=width, edgecolor=new_palette[2], \
                hatch=patterns[0]*4, linewidth=1.0, zorder = 0, label='LRU Hit Rate')
    ax.bar(position, hitrates, color='none', width=width, edgecolor='k', linewidth=0.5)
    
   
    ax.bar([x + pos_gap + width for x in position], new_hitrates, color='none', width=width, edgecolor=new_palette[3], \
                hatch=patterns[2]*4, linewidth=1.0, zorder = 0, label='LF Hit Rate')
    ax.bar([x + pos_gap + width for x in position], new_hitrates, color='none', width=width, edgecolor='k', linewidth=0.5)   
    
    ax.bar([x + 4*pos_gap + 2*width for x in position], bandwidth_saved_ratios, color='none', width=width, edgecolor=new_palette[4], \
                hatch=patterns[0]*4, linewidth=1.0, zorder = 0, label='LRU Efficiency')
    ax.bar([x + 4*pos_gap + 2*width for x in position], bandwidth_saved_ratios, color='none', width=width, edgecolor='k', linewidth=0.5)
    

    ax.bar([x + 5*pos_gap + 3*width for x in position], new_bandwidth_saved_ratios, color='none', width=width, edgecolor=new_palette[5], \
                hatch=patterns[2]*4, linewidth=1.0, zorder = 0, label='LF Efficiency')
    ax.bar([x + 5*pos_gap + 3*width for x in position], new_bandwidth_saved_ratios, color='none', width=width, edgecolor='k', linewidth=0.5)   
    

    ax2.bar(position, hitrates, color='none', width=width, edgecolor=new_palette[2], \
                hatch=patterns[0]*4, linewidth=1.0, zorder = 0, label='LRU Hit Rate')
    ax2.bar(position, hitrates, color='none', width=width, edgecolor='k', linewidth=0.5)
    
    

    ax2.bar([x + pos_gap + width for x in position], new_hitrates, color='none', width=width, edgecolor=new_palette[3], \
                hatch=patterns[2]*4, linewidth=1.0, zorder = 0, label='LF Hit Rate')
    ax2.bar([x + pos_gap + width for x in position], new_hitrates, color='none', width=width, edgecolor='k', linewidth=0.5)   
    
    ax2.bar([x + 4*pos_gap + 2*width for x in position], bandwidth_saved_ratios, color='none', width=width, edgecolor=new_palette[4], \
                hatch=patterns[0]*4, linewidth=1.0, zorder = 0, label='LRU Efficiency')
    ax2.bar([x + 4*pos_gap + 2*width for x in position], bandwidth_saved_ratios, color='none', width=width, edgecolor='k', linewidth=0.5)
    

    ax2.bar([x + 5*pos_gap + 3*width for x in position], new_bandwidth_saved_ratios, color='none', width=width, edgecolor=new_palette[5], \
                hatch=patterns[2]*4, linewidth=1.0, zorder = 0, label='LF Efficiency')
    ax2.bar([x + 5*pos_gap + 3*width for x in position], new_bandwidth_saved_ratios, color='none', width=width, edgecolor='k', linewidth=0.5)   
    

    ax.set_ylim(-0.02, 0.5)  # outliers only
    ax2.set_ylim(-1.0, -0.48)  # most of the data

    ax.spines['bottom'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    ax.xaxis.tick_top()
    ax.tick_params(labeltop=False)  # don't put tick labels at the top
    ax2.xaxis.tick_bottom()

    d = .015
    kwargs = dict(transform=ax.transAxes, color='k', clip_on=False)
    ax.plot((-d, +d), (-d, +d), **kwargs)        # top-left diagonal
    ax.plot((1 - d, 1 + d), (-d, +d), **kwargs)  # top-right diagonal
    ax.plot([-0.5*width, position[-1]+ 5*pos_gap + 4*width + 0.5*width], [0, 0], color='k', linewidth=1)
    kwargs.update(transform=ax2.transAxes)  # switch to the bottom axes
    ax2.plot((-d, +d), (1 - d, 1 + d), **kwargs)  # bottom-left diagonal
    ax2.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)  # bottom-right diagonal
    xticks_pos = [position[group_id]+ 2*width+ 2.5*pos_gap for group_id in range(len(hitrates))]
    ax2.set_xticks(xticks_pos)
    ax2.set_xticklabels(['Naive Cache', 'Transcoding', 'Enhanced \n Transcoding'], fontsize=20)
    ax.set_yticks([0,0.2,0.4])
    ax.set_yticklabels([0,0.2,0.4], fontsize=20)
    ax2.set_yticks([-0.8, -0.6])
    ax2.set_yticklabels([-0.8, -0.6], fontsize=20)
    # plt.yticks(np.arange(int(y_axis_lower/0.1)*0.1, 0.21, 0.1), fontsize=20)
    # plt.axis([-0.5*width, position[-1]+ 5*pos_gap + 4*width + 0.5*width, y_axis_lower, y_axis_upper+0.2])
    # ax.ylabel('Ratio', fontsize=20)
    ax.set_xlim([-0.5*width, position[-1]+ 5*pos_gap + 4*width + 0.5*width])

    ax2.legend(loc='lower left', fontsize=20, ncol=1)
    # plt.close()

    

    # Figure 2: bandwidth save
    # q = plt.figure(figsize=(9, 7))
    # plt.bar(position, bandwidth_saved_ratios, color='none', width=width, edgecolor=new_palette[4], \
    #             hatch=patterns[4]*6, linewidth=1.0, zorder = 0, label='Hit Rate')
    # plt.bar(position, bandwidth_saved_ratios, color='none', width=width, edgecolor='k', linewidth=0.5)
    # plt.bar([x + pos_gap for x in position], new_bandwidth_saved_ratios, color='none', width=width, edgecolor=new_palette[5], \
    #             hatch=patterns[5]*6, linewidth=1.0, zorder = 0, label='Traffic Efficiency Ratio')
    # plt.bar([x + pos_gap for x in position], new_bandwidth_saved_ratios, color='none', width=width, edgecolor='k', linewidth=0.5)   
    
    # xticks_pos = [position[group_id]+width+0.5*(pos_gap-width) for group_id in range(len(hitrates))]
    # plt.xticks(xticks_pos, ['Naive Cache', 'Edge \n Transcoding', 'Enhanced Edge \n Transcoding'], fontsize=20)
    # plt.yticks(np.arange(0, y_axis_upper, 0.05), fontsize=20)
    # plt.axis([-0.5*width, position[-1]+ pos_gap + 1.5*width, min(bandwidth_saved_ratios), y_axis_upper])
    # plt.ylabel('Ratio', fontsize=20)

    # plt.legend(loc='upper right', fontsize=20, ncol=2)
    # plt.close()
    # f.tight_layout()

    return f


def plot_curve_unlimited():
    line_type = ['-', '--']
    times = []
    bits = []
    sizes = []
    transes = []
    for method in [0,1,2,3]:
        time, bit, size, trans = load_unlimited_curve(method, COOR, OPTIMIZE)
        times.append(time)
        bits.append(bit)
        sizes.append(size)
        transes.append(trans)

    labels = ['Naive', \
            'Transcoding', \
            'E-Transcoding', \
            'U-Transcoding']
    p = plt.figure(figsize=(9, 7))
    for i in range(len(times)):
        plt.plot(times[i], bits[i], color=new_palette[i%4], linewidth=2.0, linestyle=line_type[0],\
                label=labels[i])
        # plt.plot(times[i], transes[i], color=new_palette[i%4], linewidth=2.0, linestyle=line_type[1],\
        #         label=labels[2*i+1])

    y_axis_upper = int(max(bits[0]))*1.1
    y_axis_lower = 0.0
    plt.xticks(range(0, int(times[-1][-1]), 100), fontsize=22)
    plt.yticks(np.arange(0, y_axis_upper, 50000), [int(x/10000) for x in np.arange(0, y_axis_upper, 50000)], fontsize=20)
    plt.axis([0, times[-1][-1], y_axis_lower, y_axis_upper])
    plt.xlabel('Time (s)', fontsize=22)
    plt.ylabel(r'x10 GB', fontsize=22)
    plt.legend(loc='upper left', fontsize=24, ncol=1)
    plt.close()
    return p 

def plot_curve_duration():
    line_type = ['-', '--']
    times = []
    bits = []
    sizes = []
    transes = []
    for method in [0,1,2,3]:
        time, bit, size, trans = load_duration_curve(method, COOR, OPTIMIZE)
        times.append(time)
        bits.append(bit)
        sizes.append(size)
        transes.append(trans)

    labels = ['Naive', \
            'Transcoding', \
            'E-Transcoding', \
            'U-Transcoding']
    p = plt.figure(figsize=(9, 7))
    for i in range(len(times)):
        plt.plot(times[i], bits[i], color=new_palette[i%4], linewidth=2.0, linestyle=line_type[0],\
                label=labels[i])
        # plt.plot(times[i], transes[i], color=new_palette[i%4], linewidth=2.0, linestyle=line_type[1],\
        #         label=labels[2*i+1])

    y_axis_upper = int(max(bits[0]))*1.3
    y_axis_lower = 0.0
    plt.xticks(range(0, int(times[-1][-1]), 100), fontsize=22)
    plt.yticks(np.arange(0, y_axis_upper, 5000), [x/1000 for x in np.arange(0, y_axis_upper, 5000)], fontsize=20)
    plt.axis([0, times[-1][-1], y_axis_lower, y_axis_upper])
    plt.xlabel('Time (s)', fontsize=22)
    plt.ylabel('GB', fontsize=22)
    plt.legend(loc='upper right', fontsize=24, ncol=1)
    plt.close()
    return p 

def load_unlimited_curve(method, coor, optimize):
    ratio_path = './cache_ratio_results/'
    current_case_path = ratio_path + 'unlimited/'
    curve_file = current_case_path + 'm' + str(method) + '_coor' + str(coor) + '_opt' + str(optimize) + '.txt'
    
    time = []
    size = []
    bits = []
    trans = []
    with open(curve_file, 'r') as cf:
        for line in cf:
            line = line.strip('\n').split(' ')
            time.append(float(line[0]))
            bits.append(float(line[1])/8)
            size.append(float(line[2]))
            trans.append(float(line[3]))
    offset = time[0]
    time = [x-offset for x in time]
    return time, bits, size, trans

def load_duration_curve(method, coor, optimize):
    ratio_path = './cache_ratio_results/'
    current_case_path = ratio_path + 'duration/'
    curve_file = current_case_path + 'm' + str(method) + '_coor' + str(coor) + '_opt' + str(optimize) + '.txt'
    
    time = []
    size = []
    bits = []
    trans = []
    with open(curve_file, 'r') as cf:
        for line in cf:
            line = line.strip('\n').split(' ')
            time.append(float(line[0]))
            bits.append(float(line[1])/8)
            size.append(float(line[2]))
            trans.append(float(line[3]))
    offset = time[0]
    time = [x-offset for x in time]
    return time, bits, size, trans

def plot_bar_unlimited(hitrates, bandwidth_saved_ratios, size_list, trans_ratio):
    hitrates = [float(x) for x in hitrates]
    bandwidth_saved_ratios = [float(x) for x in bandwidth_saved_ratios]
    size_list = [int(x) for x in size_list]
    trans_ratio = [float(x) for x in trans_ratio]
    y_axis_upper = max(hitrates)*1.05

    width = 0.15  # the width of the bars
    pos_gap = 0.04

    position = []
    curr_pos = pos_gap
    for u_id in range(len(hitrates)):
        position.append(curr_pos)
        curr_pos += 3*width + 2*pos_gap + 4*(pos_gap)

    p = plt.figure(figsize=(9, 7))
    plt.bar(position, hitrates, color=new_palette[0], width=width, edgecolor='k', linewidth = 1, \
                label='Hit Rate')
    # plt.bar(position, hitrates, color='none', width=width, edgecolor='k', linewidth=0.5)

    
    plt.bar([x + width + pos_gap for x in position], bandwidth_saved_ratios, color=new_palette[1], width=width, edgecolor='k', linewidth=1, \
                label='Network Efficiency')
    # plt.bar([x + width + pos_gap for x in position], bandwidth_saved_ratios, color='none', width=width, edgecolor='k', linewidth=0.5)   
    
    plt.bar([x + 2*width + 2*pos_gap for x in position], trans_ratio, color=new_palette[3], width=width, edgecolor='k', linewidth=1, \
                label='Transcoding Rate')
    # plt.bar([x + 2*width + 2*pos_gap for x in position], trans_ratio, color='none', width=width, edgecolor='k', linewidth=0.5)


    plt.plot([position[0]-2,position[-1]+4], [1,1], '--', linewidth=1.5, color='k')
    xticks_pos = [position[group_id]+width+pos_gap for group_id in range(len(hitrates))]
    plt.xticks(xticks_pos, ['Naive', 'Transcoding', 'Enhanced \n Transcoding', 'Ultimate \n Transcoding'], fontsize=20)
    plt.yticks(np.arange(0.8, y_axis_upper, 0.1), fontsize=20)
    plt.axis([-0.5*width, position[-1]+ 2*pos_gap + 3*width, 0.8, y_axis_upper])
    plt.ylabel('Ratio', fontsize=22)

    plt.legend(loc='upper right', fontsize=18, ncol=2)
    plt.close()
    return p


if __name__ == '__main__':
    main()
