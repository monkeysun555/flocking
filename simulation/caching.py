import numpy as np
import os
from config import Config
from collections import deque

# CACHE_METHOD = 7            # 0: cache all, 1. Download highest rate from server, 2: simpe transcoding (high to low)
#                             # 3: Limited size, LRU, 4: limited size, highest rate from server 5 limited size, LRU, transcoding
#                             # 7: 
# REPRE_METHOD = 1            # 0: REPRE 1: NOT REPRE 2: GLOBAL_NOT, 3 GLOBAL_W_NOT   
N_USERS = 48 
NUM_GLOBAL_NOT = 2            # Number of global lowest users, 4 is best                

class edge_cache(object):
    def __init__(self, coor, optimize, cache_method, cache_size, repre_method = 2, interval=40):     # 2 is best
        self.cache_method = cache_method
        self.current_size = 0
        self.trace = None
        self.repre_method = repre_method
        self.cache_size = cache_size
        self.coor = coor
        self.optimize = optimize    
        self.time_gap = Config.ms_in_s
        self.curr_bitsize = 0.0
        self.interval = interval*Config.ms_in_s

    def do_caching(self):
        ratio_path = './cache_ratio_results/'
        
        n_request_tiles = len(self.trace)
        print("Total len is: ", n_request_tiles)
        cache_count = 0.0
        processed_seq = sorted(self.trace)
        num_bit_transmitted = 0.0
        num_bit_total = 0.0
        num_of_transcoding = 0.0
        if self.cache_method == 0:
            # Cache all
            current_case_path = ratio_path + 'unlimited/'
            ratio_write = open(current_case_path + 'm0_coor' + str(self.coor) + '_opt' + str(self.optimize) + '.txt', 'w')
            next_time = processed_seq[0][0]

            self.cache = dict()
            for t_idx in range(len(processed_seq)): 
                if t_idx% int(0.05*n_request_tiles)==0:
                    print(t_idx)
                time = processed_seq[t_idx][0]
                if time >= next_time:
                    ratio_write.write(str(time/Config.ms_in_s) + ' ' + str(self.curr_bitsize) + ' ' + str(self.current_size) + ' ' + str(num_of_transcoding))
                    ratio_write.write('\n')
                    next_time += self.time_gap
                
                tile = processed_seq[t_idx]
                seg_idx = tile[1][0]
                tile_idx = tile[1][1]
                rate = tile[1][2]
                num_bit_total += rate * Config.tile_ratio
                if (seg_idx, tile_idx, rate) in self.cache:
                    cache_count += 1.0
                    continue
                self.cache[(seg_idx, tile_idx, rate)] = 1
                self.current_size += 1
                num_bit_transmitted += rate * Config.tile_ratio
                self.curr_bitsize += rate * Config.tile_ratio

        elif self.cache_method == 1:
            # Do caching based transcoding
            current_case_path = ratio_path + 'unlimited/'
            ratio_write = open(current_case_path + 'm1_coor' + str(self.coor) + '_opt' + str(self.optimize) + '.txt', 'w')
            next_time = processed_seq[0][0]

            self.cache = dict()
            for t_idx in range(len(processed_seq)):
                if t_idx% int(0.05*n_request_tiles)==0:
                    print(t_idx)
                # Write size and transcoding
                time = processed_seq[t_idx][0]
                if time >= next_time:
                    ratio_write.write(str(time/Config.ms_in_s) + ' ' + str(self.curr_bitsize) + ' ' + str(self.current_size) + ' ' + str(num_of_transcoding))
                    ratio_write.write('\n')
                    next_time += self.time_gap
                tile = processed_seq[t_idx] 
                seg_idx = tile[1][0]
                tile_idx = tile[1][1]
                rate = tile[1][2]
                num_bit_total += rate * Config.tile_ratio
                if (seg_idx, tile_idx) in self.cache:
                    if rate <= self.cache[(seg_idx, tile_idx)]:
                        cache_count += 1.0
                        if rate < self.cache[(seg_idx, tile_idx)]:
                            num_of_transcoding += 1.0
                        continue
                    else:
                        self.curr_bitsize -= self.cache[(seg_idx, tile_idx)] * Config.tile_ratio
                        self.cache[(seg_idx, tile_idx)] = rate
                        num_bit_transmitted += rate * Config.tile_ratio
                        self.curr_bitsize += rate * Config.tile_ratio
                else:
                    self.cache[(seg_idx, tile_idx)] = rate
                    self.current_size += 1
                    num_bit_transmitted += rate * Config.tile_ratio
                    self.curr_bitsize += rate * Config.tile_ratio

        elif self.cache_method == 2:
            # Download highest rate from server
            current_case_path = ratio_path + 'unlimited/'
            ratio_write = open(current_case_path + 'm2_coor' + str(self.coor) + '_opt' + str(self.optimize) + '.txt', 'w')
            next_time = processed_seq[0][0]

            self.cache = dict()
            for t_idx in range(len(processed_seq)):
                if t_idx% int(0.05*n_request_tiles)==0:
                    print(t_idx)
                time = processed_seq[t_idx][0]
                if time >= next_time:
                    ratio_write.write(str(time/Config.ms_in_s) + ' ' + str(self.curr_bitsize) + ' ' + str(self.current_size) + ' ' + str(num_of_transcoding))
                    ratio_write.write('\n')
                    next_time += self.time_gap

                tile = processed_seq[t_idx] 
                seg_idx = tile[1][0]
                tile_idx = tile[1][1]
                rate = tile[1][2]
                num_bit_total += rate * Config.tile_ratio

                if (seg_idx, tile_idx) in self.cache:
                    if rate <= self.cache[(seg_idx, tile_idx)]:
                        cache_count += 1.0
                        if rate < self.cache[(seg_idx, tile_idx)]:
                            num_of_transcoding += 1.0
                        continue
                    else:
                        print(rate, self.cache[(seg_idx, tile_idx)])
                        assert 0 == 1
                else:
                    self.cache[(seg_idx, tile_idx)] = Config.bitrate[-1]
                    self.current_size += 1
                    num_bit_transmitted += Config.bitrate[-1] * Config.tile_ratio
                    # if rate < Config.bitrate[-1]:
                    #     num_of_transcoding += 1.0
                    self.curr_bitsize += Config.bitrate[-1] * Config.tile_ratio

        elif self.cache_method == 3:
            # Download highest rate for all tiles from server
            current_case_path = ratio_path + 'unlimited/'
            ratio_write = open(current_case_path + 'm3_coor' + str(self.coor) + '_opt' + str(self.optimize) + '.txt', 'w')
            next_time = processed_seq[0][0]

            self.cache = dict()
            for t_idx in range(len(processed_seq)):
                if t_idx% int(0.05*n_request_tiles)==0:
                    print(t_idx)
                time = processed_seq[t_idx][0]
                if time >= next_time:
                    ratio_write.write(str(time/Config.ms_in_s) + ' ' + str(self.curr_bitsize)+ ' ' + str(self.current_size)  + ' ' + str(num_of_transcoding))
                    ratio_write.write('\n')
                    next_time += self.time_gap

                tile = processed_seq[t_idx] 
                seg_idx = tile[1][0]
                tile_idx = tile[1][1]
                rate = tile[1][2]
                num_bit_total += rate * Config.tile_ratio

                if seg_idx not in self.cache:
                    # Assume all tiles are cached
                    self.cache[seg_idx] = Config.bitrate[-1]
                    num_bit_transmitted += Config.bitrate[-1]
                    self.current_size += Config.n_yaw * Config.n_pitch
                    self.curr_bitsize += Config.bitrate[-1]

                assert seg_idx in self.cache
                cache_count += 1.0
                if rate < Config.bitrate[-1]:
                    num_of_transcoding += 1.0
        # Limited size
        elif self.cache_method == 4:
            # LRU, limited size
            self.cache = deque()
            for t_idx in range(len(processed_seq)): 
                if t_idx% int(0.05*n_request_tiles)==0:
                    print(t_idx)
                tile = processed_seq[t_idx]
                num_bit_total += tile[1][2] * Config.tile_ratio
                if self.cache.count(tile[1]) > 0:
                    cache_count += 1.0
                    continue
                num_bit_transmitted += tile[1][2] * Config.tile_ratio
                if self.current_size < self.cache_size:
                    self.cache.append(tile[1])
                    self.current_size += 1
                else:
                    assert self.current_size == self.cache_size
                    self.cache.popleft()
                    self.cache.append(tile[1])

        elif self.cache_method == 5:
            # LRU, do caching based transcoding
            self.cache = []
            rate_list = []
            for t_idx in range(len(processed_seq)):
                if t_idx% int(0.05*n_request_tiles)==0:
                    print(t_idx)
                tile = processed_seq[t_idx] 
                seg_idx = tile[1][0]
                tile_idx = tile[1][1]
                rate = tile[1][2]
                num_bit_total += rate * Config.tile_ratio

                if (seg_idx, tile_idx) in self.cache:
                    if rate <= rate_list[self.cache.index((seg_idx, tile_idx))]:
                        cache_count += 1.0
                        continue
                    else:
                        index = self.cache.index((seg_idx, tile_idx))
                        del self.cache[index]
                        del rate_list[index]
                        self.cache.append((seg_idx, tile_idx))
                        rate_list.append(rate)
                        num_bit_transmitted += rate * Config.tile_ratio

                else:
                    num_bit_transmitted += rate * Config.tile_ratio
                    if self.current_size < self.cache_size:
                        self.cache.append((seg_idx, tile_idx))
                        rate_list.append(rate)
                        self.current_size += 1
                    else:
                        assert self.current_size == self.cache_size
                        del self.cache[0]
                        del rate_list[0]
                        self.cache.append((seg_idx, tile_idx))
                        rate_list.append(rate)

        elif self.cache_method == 6:
            # LRU, highest rate
            self.cache = deque()
            for t_idx in range(len(processed_seq)):
                if t_idx% int(0.05*n_request_tiles)==0:
                    print(t_idx)
                tile = processed_seq[t_idx] 
                seg_idx = tile[1][0]
                tile_idx = tile[1][1]
                rate = tile[1][2]
                num_bit_total += rate * Config.tile_ratio
                if self.cache.count((seg_idx, tile_idx)) > 0:
                    cache_count += 1.0
                    continue
                num_bit_transmitted += Config.bitrate[-1] * Config.tile_ratio
                if self.current_size < self.cache_size:
                    self.cache.append((seg_idx, tile_idx))
                    self.current_size += 1
                else:
                    assert self.current_size == self.cache_size
                    self.cache.popleft()
                    self.cache.append((seg_idx, tile_idx))


        elif self.cache_method == 7:
            # Using representative, limited size
            represent_trace, not_represent_trace, global_not_represent_trace, global_not_w_represent_trace = self.load_represent()

            # Represent
            if self.repre_method == 0:
                curr_repre = represent_trace[0][1]
                del represent_trace[0]
                next_update_time = represent_trace[0][0]

            # Not repre
            elif self.repre_method == 1:
                curr_not_repre = not_represent_trace[0][1]
                del represent_trace[0]
                next_update_time = not_represent_trace[0][0]

            # Global not 
            elif self.repre_method == 2:
                curr_global_not_repre = global_not_represent_trace[0][1]
                del global_not_represent_trace[0]
                next_update_time = global_not_represent_trace[0][0]

            elif self.repre_method == 3:
                curr_global_not_w_repre = global_not_w_represent_trace[0][1]
                del global_not_w_represent_trace[0]
                next_update_time = global_not_w_represent_trace[0][0]

            self.cache = deque()
            for t_idx in range(len(processed_seq)): 
                if t_idx% int(0.05*n_request_tiles)==0:
                    print(t_idx)
                tile = processed_seq[t_idx]
                time = tile[0]
                u_id = tile[2]
                num_bit_total += tile[1][2] * Config.tile_ratio

                if time >= next_update_time:
                    # Repre
                    if self.repre_method == 0:
                        curr_repre = represent_trace[0][1]
                        del represent_trace[0]
                        if len(represent_trace):
                            next_update_time = represent_trace[0][0]
                        else:
                            next_update_time = float('inf')

                    # Not repre
                    elif self.repre_method == 1:
                        curr_not_repre = not_represent_trace[0][1]
                        del not_represent_trace[0]
                        if len(not_represent_trace):
                            next_update_time = not_represent_trace[0][0]
                        else:
                            next_update_time = float('inf')
                    
                    # Global not
                    elif self.repre_method == 2:
                        curr_global_not_repre = global_not_represent_trace[0][1]
                        del global_not_represent_trace[0]
                        if len(global_not_represent_trace):
                            next_update_time = global_not_represent_trace[0][0]
                        else:
                            next_update_time = float('inf')

                    elif self.repre_method == 3:
                        curr_global_not_w_repre = global_not_w_represent_trace[0][1]
                        del global_not_w_represent_trace[0]
                        if len(global_not_w_represent_trace):
                            next_update_time = global_not_w_represent_trace[0][0]
                        else:
                            next_update_time = float('inf')

                if self.cache.count(tile[1]) > 0:
                    cache_count += 1.0
                    continue
                # if u_id in curr_repre:
                num_bit_transmitted += tile[1][2] * Config.tile_ratio
                if (self.repre_method == 0 and u_id in curr_repre) or (self.repre_method == 1 and u_id not in curr_not_repre) or \
                    (self.repre_method == 2 and u_id not in curr_global_not_repre) or (self.repre_method == 3 and u_id not in curr_global_not_w_repre) :
                    if self.current_size < self.cache_size:
                        self.cache.append(tile[1])
                        self.current_size += 1
                    else:
                        assert self.current_size == self.cache_size
                        self.cache.popleft()
                        self.cache.append(tile[1])

        elif self.cache_method == 8:
            # repre, do caching based transcoding
            represent_trace, not_represent_trace, global_not_represent_trace, global_not_w_represent_trace = self.load_represent()

            if self.repre_method == 0:
                curr_repre = represent_trace[0][1]
                del represent_trace[0]
                next_update_time = represent_trace[0][0]

            # Not repre
            elif self.repre_method == 1:
                curr_not_repre = not_represent_trace[0][1]
                del represent_trace[0]
                next_update_time = not_represent_trace[0][0]

            # Global not 
            elif self.repre_method == 2:
                curr_global_not_repre = global_not_represent_trace[0][1]
                del global_not_represent_trace[0]
                next_update_time = global_not_represent_trace[0][0]

            elif self.repre_method == 3:
                curr_global_not_w_repre = global_not_w_represent_trace[0][1]
                del global_not_w_represent_trace[0]
                next_update_time = global_not_w_represent_trace[0][0]

            self.cache = []
            rate_list = []
            for t_idx in range(len(processed_seq)):
                if t_idx% int(0.05*n_request_tiles)==0:
                    print(t_idx)
                tile = processed_seq[t_idx] 
                time = tile[0]
                u_id = tile[2]
                seg_idx = tile[1][0]
                tile_idx = tile[1][1]
                rate = tile[1][2]
                num_bit_total += rate * Config.tile_ratio

                if time >= next_update_time:
                    # Repre
                    if self.repre_method == 0:
                        curr_repre = represent_trace[0][1]
                        del represent_trace[0]
                        if len(represent_trace):
                            next_update_time = represent_trace[0][0]
                        else:
                            next_update_time = float('inf')

                    # Not repre
                    elif self.repre_method == 1:
                        curr_not_repre = not_represent_trace[0][1]
                        del not_represent_trace[0]
                        if len(not_represent_trace):
                            next_update_time = not_represent_trace[0][0]
                        else:
                            next_update_time = float('inf')
                    
                    # Global not
                    elif self.repre_method == 2:
                        curr_global_not_repre = global_not_represent_trace[0][1]
                        del global_not_represent_trace[0]
                        if len(global_not_represent_trace):
                            next_update_time = global_not_represent_trace[0][0]
                        else:
                            next_update_time = float('inf')

                    elif self.repre_method == 3:
                        curr_global_not_w_repre = global_not_w_represent_trace[0][1]
                        del global_not_w_represent_trace[0]
                        if len(global_not_w_represent_trace):
                            next_update_time = global_not_w_represent_trace[0][0]
                        else:
                            next_update_time = float('inf')

                if (seg_idx, tile_idx) in self.cache:
                    if rate <= rate_list[self.cache.index((seg_idx, tile_idx))]:
                        cache_count += 1.0
                        continue
                    else:
                        num_bit_transmitted += rate * Config.tile_ratio
                        if (self.repre_method == 0 and u_id in curr_repre) or (self.repre_method == 1 and u_id not in curr_not_repre)\
                            or (self.repre_method == 2 and u_id not in curr_global_not_repre) or (self.repre_method == 3 and u_id not in curr_global_not_w_repre) :
                            index = self.cache.index((seg_idx, tile_idx))
                            del self.cache[index]
                            del rate_list[index]
                            self.cache.append((seg_idx, tile_idx))
                            rate_list.append(rate)

                else:
                    num_bit_transmitted += rate * Config.tile_ratio
                    if (self.repre_method == 0 and u_id in curr_repre) or (self.repre_method == 1 and u_id not in curr_not_repre) \
                         or (self.repre_method == 2 and u_id not in curr_global_not_repre) or (self.repre_method == 3 and u_id not in curr_global_not_w_repre) :
                        if self.current_size < self.cache_size:
                            self.cache.append((seg_idx, tile_idx))
                            rate_list.append(rate)
                            self.current_size += 1
                        else:
                            assert self.current_size == self.cache_size
                            del self.cache[0]
                            del rate_list[0]
                            self.cache.append((seg_idx, tile_idx))
                            rate_list.append(rate)

        elif self.cache_method == 9:
            # repre, highest rate
            represent_trace, not_represent_trace, global_not_represent_trace, global_not_w_represent_trace = self.load_represent()

            if self.repre_method == 0:
                curr_repre = represent_trace[0][1]
                del represent_trace[0]
                next_update_time = represent_trace[0][0]

            # Not repre
            elif self.repre_method == 1:
                curr_not_repre = not_represent_trace[0][1]
                del represent_trace[0]
                next_update_time = not_represent_trace[0][0]

            # Global not 
            elif self.repre_method == 2:
                curr_global_not_repre = global_not_represent_trace[0][1]
                del global_not_represent_trace[0]
                next_update_time = global_not_represent_trace[0][0]

            elif self.repre_method == 3:
                curr_global_not_w_repre = global_not_w_represent_trace[0][1]
                del global_not_w_represent_trace[0]
                next_update_time = global_not_w_represent_trace[0][0]

            self.cache = deque()
            for t_idx in range(len(processed_seq)):
                if t_idx% int(0.05*n_request_tiles)==0:
                    print(t_idx)
                tile = processed_seq[t_idx]
                time = tile[0]
                u_id = tile[2]
                seg_idx = tile[1][0]
                tile_idx = tile[1][1]
                rate = tile[1][2]
                num_bit_total += rate * Config.tile_ratio
                if time >= next_update_time:
                    # Repre
                    if self.repre_method == 0:
                        curr_repre = represent_trace[0][1]
                        del represent_trace[0]
                        if len(represent_trace):
                            next_update_time = represent_trace[0][0]
                        else:
                            next_update_time = float('inf')

                    # Not repre
                    elif self.repre_method == 1:
                        curr_not_repre = not_represent_trace[0][1]
                        del not_represent_trace[0]
                        if len(not_represent_trace):
                            next_update_time = not_represent_trace[0][0]
                        else:
                            next_update_time = float('inf')
                    
                    # Global not
                    elif self.repre_method == 2:
                        curr_global_not_repre = global_not_represent_trace[0][1]
                        del global_not_represent_trace[0]
                        if len(global_not_represent_trace):
                            next_update_time = global_not_represent_trace[0][0]
                        else:
                            next_update_time = float('inf')

                    elif self.repre_method == 3:
                        curr_global_not_w_repre = global_not_w_represent_trace[0][1]
                        del global_not_w_represent_trace[0]
                        if len(global_not_w_represent_trace):
                            next_update_time = global_not_w_represent_trace[0][0]
                        else:
                            next_update_time = float('inf')

                if self.cache.count((seg_idx, tile_idx)) > 0:
                    cache_count += 1.0
                    continue
                # if u_id in curr_repre:
                num_bit_transmitted += Config.bitrate[-1] * Config.tile_ratio
                if (self.repre_method == 0 and u_id  in curr_repre) or (self.repre_method == 1 and u_id not in curr_not_repre) \
                    or (self.repre_method == 2 and u_id not in curr_global_not_repre) or (self.repre_method == 3 and u_id not in curr_global_not_w_repre):
                    if self.current_size < self.cache_size:
                        self.cache.append((seg_idx, tile_idx))
                        self.current_size += 1
                    else:
                        assert self.current_size == self.cache_size
                        self.cache.popleft()
                        self.cache.append((seg_idx, tile_idx))


        # Limited size in bit
        elif self.cache_method == 10:
            # LRU, limited size, naive
            self.cache = deque()
            for t_idx in range(len(processed_seq)): 
                if t_idx% int(0.05*n_request_tiles)==0:
                    print(t_idx)
                tile = processed_seq[t_idx]
                seg_idx = tile[1][0]
                tile_idx = tile[1][1]
                rate = tile[1][2]
                num_bit_total += rate * Config.tile_ratio
                if self.cache.count(tile[1]) > 0:
                    cache_count += 1.0
                    continue
                num_bit_transmitted += tile[1][2] * Config.tile_ratio
                curr_tile_size = tile[1][2] * Config.tile_ratio
                while self.cache and self.cache_size - self.current_size < curr_tile_size:
                    pop_tile = self.cache.popleft()
                    pop_rate = pop_tile[2]
                    pop_tile_size = pop_rate * Config.tile_ratio
                    self.current_size -= pop_tile_size
                self.cache.append(tile[1])
                self.current_size += curr_tile_size

        elif self.cache_method == 11:
            # LRU, do caching based transcoding, 
            self.cache = []
            rate_list = []
            for t_idx in range(len(processed_seq)):
                if t_idx% int(0.05*n_request_tiles)==0:
                    print(t_idx)
                tile = processed_seq[t_idx] 
                seg_idx = tile[1][0]
                tile_idx = tile[1][1]
                rate = tile[1][2]
                num_bit_total += rate * Config.tile_ratio
                curr_tile_size = rate * Config.tile_ratio
                if (seg_idx, tile_idx) in self.cache:
                    if rate <= rate_list[self.cache.index((seg_idx, tile_idx))]:
                        cache_count += 1.0
                        continue
                    else:
                        index = self.cache.index((seg_idx, tile_idx))
                        previous_tile_size = rate_list[index] * Config.tile_ratio 
                        del self.cache[index]
                        del rate_list[index]
                        while len(self.cache) and self.cache_size - self.current_size < curr_tile_size - previous_tile_size:
                            self.current_size -= rate_list[0] * Config.tile_ratio
                            del self.cache[0]
                            del rate_list[0]
                        self.cache.append((seg_idx, tile_idx))
                        rate_list.append(rate)
                        self.current_size += curr_tile_size - previous_tile_size
                        num_bit_transmitted += rate * Config.tile_ratio

                else:
                    num_bit_transmitted += rate * Config.tile_ratio
                    while len(self.cache) and self.cache_size - self.current_size < curr_tile_size:
                        self.current_size -= rate_list[0] * Config.tile_ratio
                        del self.cache[0]
                        del rate_list[0]
                    self.cache.append((seg_idx, tile_idx))
                    rate_list.append(rate)
                    self.current_size += curr_tile_size
                

        elif self.cache_method == 12:
            # LRU, highest rate
            self.cache = deque()
            for t_idx in range(len(processed_seq)):
                if t_idx% int(0.05*n_request_tiles)==0:
                    print(t_idx)
                tile = processed_seq[t_idx] 
                seg_idx = tile[1][0]
                tile_idx = tile[1][1]
                rate = tile[1][2]
                num_bit_total += rate * Config.tile_ratio
                if self.cache.count((seg_idx, tile_idx)) > 0:
                    cache_count += 1.0
                    continue
                num_bit_transmitted += Config.bitrate[-1] * Config.tile_ratio
                curr_tile_size = rate * Config.tile_ratio
                while self.cache and self.cache_size - self.current_size < curr_tile_size:
                    pop_tile = self.cache.popleft()
                    pop_tile_size = Config.bitrate[-1] * Config.tile_ratio
                    self.current_size -= pop_tile_size
     
                self.cache.append((seg_idx, tile_idx))
                self.current_size += Config.bitrate[-1] * Config.tile_ratio
        
        elif self.cache_method == 13:
            # Using representative, limited size
            represent_trace, not_represent_trace, global_not_represent_trace, global_not_w_represent_trace = self.load_represent()

            # Represent
            if self.repre_method == 0:
                curr_repre = represent_trace[0][1]
                del represent_trace[0]
                next_update_time = represent_trace[0][0]

            # Not repre
            elif self.repre_method == 1:
                curr_not_repre = not_represent_trace[0][1]
                del represent_trace[0]
                next_update_time = not_represent_trace[0][0]

            # Global not 
            elif self.repre_method == 2:
                curr_global_not_repre = global_not_represent_trace[0][1]
                del global_not_represent_trace[0]
                next_update_time = global_not_represent_trace[0][0]

            elif self.repre_method == 3:
                curr_global_not_w_repre = global_not_w_represent_trace[0][1]
                del global_not_w_represent_trace[0]
                next_update_time = global_not_w_represent_trace[0][0]

            self.cache = deque()
            for t_idx in range(len(processed_seq)): 
                if t_idx% int(0.05*n_request_tiles)==0:
                    print(t_idx)
                tile = processed_seq[t_idx]
                time = tile[0]
                u_id = tile[2]
                num_bit_total += tile[1][2] * Config.tile_ratio
                curr_tile_size = tile[1][2] * Config.tile_ratio
                if time >= next_update_time:
                    # Repre
                    if self.repre_method == 0:
                        curr_repre = represent_trace[0][1]
                        del represent_trace[0]
                        if len(represent_trace):
                            next_update_time = represent_trace[0][0]
                        else:
                            next_update_time = float('inf')

                    # Not repre
                    elif self.repre_method == 1:
                        curr_not_repre = not_represent_trace[0][1]
                        del not_represent_trace[0]
                        if len(not_represent_trace):
                            next_update_time = not_represent_trace[0][0]
                        else:
                            next_update_time = float('inf')
                    
                    # Global not
                    elif self.repre_method == 2:
                        curr_global_not_repre = global_not_represent_trace[0][1]
                        del global_not_represent_trace[0]
                        if len(global_not_represent_trace):
                            next_update_time = global_not_represent_trace[0][0]
                        else:
                            next_update_time = float('inf')

                    elif self.repre_method == 3:
                        curr_global_not_w_repre = global_not_w_represent_trace[0][1]
                        del global_not_w_represent_trace[0]
                        if len(global_not_w_represent_trace):
                            next_update_time = global_not_w_represent_trace[0][0]
                        else:
                            next_update_time = float('inf')

                if self.cache.count(tile[1]) > 0:
                    cache_count += 1.0
                    continue
                # if u_id in curr_repre:
                num_bit_transmitted += tile[1][2] * Config.tile_ratio
                if (self.repre_method == 0 and u_id in curr_repre) or (self.repre_method == 1 and u_id not in curr_not_repre) or \
                    (self.repre_method == 2 and u_id not in curr_global_not_repre) or (self.repre_method == 3 and u_id not in curr_global_not_w_repre) :
                    while self.cache and self.cache_size - self.current_size < curr_tile_size:
                        pop_tile = self.cache.popleft()
                        pop_tile_size = pop_tile[2] * Config.tile_ratio
                        self.current_size -= pop_tile_size
                    self.cache.append(tile[1])
                    self.current_size += curr_tile_size
                
        elif self.cache_method == 14:
            # repre, do caching based transcoding
            represent_trace, not_represent_trace, global_not_represent_trace, global_not_w_represent_trace = self.load_represent()

            if self.repre_method == 0:
                curr_repre = represent_trace[0][1]
                del represent_trace[0]
                next_update_time = represent_trace[0][0]

            # Not repre
            elif self.repre_method == 1:
                curr_not_repre = not_represent_trace[0][1]
                del represent_trace[0]
                next_update_time = not_represent_trace[0][0]

            # Global not 
            elif self.repre_method == 2:
                curr_global_not_repre = global_not_represent_trace[0][1]
                del global_not_represent_trace[0]
                next_update_time = global_not_represent_trace[0][0]

            elif self.repre_method == 3:
                curr_global_not_w_repre = global_not_w_represent_trace[0][1]
                del global_not_w_represent_trace[0]
                next_update_time = global_not_w_represent_trace[0][0]

            self.cache = []
            rate_list = []
            for t_idx in range(len(processed_seq)):
                if t_idx% int(0.05*n_request_tiles)==0:
                    print(t_idx)
                tile = processed_seq[t_idx] 
                time = tile[0]
                u_id = tile[2]
                seg_idx = tile[1][0]
                tile_idx = tile[1][1]
                rate = tile[1][2]
                num_bit_total += rate * Config.tile_ratio
                curr_tile_size = rate * Config.tile_ratio

                if time >= next_update_time:
                    # Repre
                    if self.repre_method == 0:
                        curr_repre = represent_trace[0][1]
                        del represent_trace[0]
                        if len(represent_trace):
                            next_update_time = represent_trace[0][0]
                        else:
                            next_update_time = float('inf')

                    # Not repre
                    elif self.repre_method == 1:
                        curr_not_repre = not_represent_trace[0][1]
                        del not_represent_trace[0]
                        if len(not_represent_trace):
                            next_update_time = not_represent_trace[0][0]
                        else:
                            next_update_time = float('inf')
                    
                    # Global not
                    elif self.repre_method == 2:
                        curr_global_not_repre = global_not_represent_trace[0][1]
                        del global_not_represent_trace[0]
                        if len(global_not_represent_trace):
                            next_update_time = global_not_represent_trace[0][0]
                        else:
                            next_update_time = float('inf')

                    elif self.repre_method == 3:
                        curr_global_not_w_repre = global_not_w_represent_trace[0][1]
                        del global_not_w_represent_trace[0]
                        if len(global_not_w_represent_trace):
                            next_update_time = global_not_w_represent_trace[0][0]
                        else:
                            next_update_time = float('inf')

                if (seg_idx, tile_idx) in self.cache:
                    if rate <= rate_list[self.cache.index((seg_idx, tile_idx))]:
                        cache_count += 1.0
                        continue
                    else:
                        num_bit_transmitted += rate * Config.tile_ratio
                        if (self.repre_method == 0 and u_id in curr_repre) or (self.repre_method == 1 and u_id not in curr_not_repre)\
                            or (self.repre_method == 2 and u_id not in curr_global_not_repre) or (self.repre_method == 3 and u_id not in curr_global_not_w_repre) :
                            index = self.cache.index((seg_idx, tile_idx))
                            previous_tile_size = rate_list[index] * Config.tile_ratio 
                            del self.cache[index]
                            del rate_list[index]
                            while len(self.cache) and self.cache_size - self.current_size < curr_tile_size - previous_tile_size:
                                self.current_size -= rate_list[0] * Config.tile_ratio
                                del self.cache[0]
                                del rate_list[0]
                            
                            self.cache.append((seg_idx, tile_idx))
                            rate_list.append(rate)
                            self.current_size += curr_tile_size - previous_tile_size

                else:
                    num_bit_transmitted += rate * Config.tile_ratio
                    if (self.repre_method == 0 and u_id in curr_repre) or (self.repre_method == 1 and u_id not in curr_not_repre) \
                     or (self.repre_method == 2 and u_id not in curr_global_not_repre) or (self.repre_method == 3 and u_id not in curr_global_not_w_repre) :
                        while len(self.cache) and self.cache_size - self.current_size < curr_tile_size:
                            self.current_size -= rate_list[0] * Config.tile_ratio
                            del self.cache[0]
                            del rate_list[0]
                        self.cache.append((seg_idx, tile_idx))
                        rate_list.append(rate)
                        self.current_size += curr_tile_size

        elif self.cache_method == 15:
            # repre, highest rate
            represent_trace, not_represent_trace, global_not_represent_trace, global_not_w_represent_trace = self.load_represent()

            if self.repre_method == 0:
                curr_repre = represent_trace[0][1]
                del represent_trace[0]
                next_update_time = represent_trace[0][0]

            # Not repre
            elif self.repre_method == 1:
                curr_not_repre = not_represent_trace[0][1]
                del represent_trace[0]
                next_update_time = not_represent_trace[0][0]

            # Global not 
            elif self.repre_method == 2:
                curr_global_not_repre = global_not_represent_trace[0][1]
                del global_not_represent_trace[0]
                next_update_time = global_not_represent_trace[0][0]

            elif self.repre_method == 3:
                curr_global_not_w_repre = global_not_w_represent_trace[0][1]
                del global_not_w_represent_trace[0]
                next_update_time = global_not_w_represent_trace[0][0]

            self.cache = deque()
            for t_idx in range(len(processed_seq)):
                if t_idx% int(0.05*n_request_tiles)==0:
                    print(t_idx)
                tile = processed_seq[t_idx]
                time = tile[0]
                u_id = tile[2]
                seg_idx = tile[1][0]
                tile_idx = tile[1][1]
                rate = tile[1][2]
                num_bit_total += rate * Config.tile_ratio
                curr_tile_size = rate * Config.tile_ratio
                if time >= next_update_time:
                    # Repre
                    if self.repre_method == 0:
                        curr_repre = represent_trace[0][1]
                        del represent_trace[0]
                        if len(represent_trace):
                            next_update_time = represent_trace[0][0]
                        else:
                            next_update_time = float('inf')

                    # Not repre
                    elif self.repre_method == 1:
                        curr_not_repre = not_represent_trace[0][1]
                        del not_represent_trace[0]
                        if len(not_represent_trace):
                            next_update_time = not_represent_trace[0][0]
                        else:
                            next_update_time = float('inf')
                    
                    # Global not
                    elif self.repre_method == 2:
                        curr_global_not_repre = global_not_represent_trace[0][1]
                        del global_not_represent_trace[0]
                        if len(global_not_represent_trace):
                            next_update_time = global_not_represent_trace[0][0]
                        else:
                            next_update_time = float('inf')

                    elif self.repre_method == 3:
                        curr_global_not_w_repre = global_not_w_represent_trace[0][1]
                        del global_not_w_represent_trace[0]
                        if len(global_not_w_represent_trace):
                            next_update_time = global_not_w_represent_trace[0][0]
                        else:
                            next_update_time = float('inf')

                if self.cache.count((seg_idx, tile_idx)) > 0:
                    cache_count += 1.0
                    continue
                # if u_id in curr_repre:
                num_bit_transmitted += Config.bitrate[-1] * Config.tile_ratio
                if (self.repre_method == 0 and u_id  in curr_repre) or (self.repre_method == 1 and u_id not in curr_not_repre) \
                    or (self.repre_method == 2 and u_id not in curr_global_not_repre) or (self.repre_method == 3 and u_id not in curr_global_not_w_repre):
                    while self.cache and self.cache_size - self.current_size < curr_tile_size:
                        pop_tile = self.cache.popleft()
                        pop_tile_size = Config.bitrate[-1] * Config.tile_ratio
                        self.current_size -= pop_tile_size
                    self.cache.append((seg_idx, tile_idx))
                    self.current_size += Config.bitrate[-1] * Config.tile_ratio
        elif self.cache_method == 16:
            # Cache all
            current_case_path = ratio_path + 'duration/'
            ratio_write = open(current_case_path + 'm0_coor' + str(self.coor) + '_opt' + str(self.optimize) + '.txt', 'w')
            next_time = processed_seq[0][0]
            curr_time = None
            self.cache = []
            time_list = []
            for t_idx in range(len(processed_seq)): 
                if t_idx% int(0.05*n_request_tiles)==0:
                    print(t_idx)
                time = processed_seq[t_idx][0]
                curr_time = time
                if time >= next_time:
                    # Do head cut
                    while len(time_list) and time_list[0] < curr_time - self.interval:
                        del time_list[0]
                        p_tile = self.cache[0]
                        self.current_size -= 1
                        self.curr_bitsize -= p_tile[2] * Config.tile_ratio
                        del self.cache[0]
                    ratio_write.write(str(time/Config.ms_in_s) + ' ' + str(self.curr_bitsize) + ' ' + str(self.current_size) + ' ' + str(num_of_transcoding))
                    ratio_write.write('\n')
                    next_time += self.time_gap
                
                tile = processed_seq[t_idx]
                seg_idx = tile[1][0]
                tile_idx = tile[1][1]
                rate = tile[1][2]
                num_bit_total += rate * Config.tile_ratio
                if (seg_idx, tile_idx, rate) in self.cache:
                    cache_count += 1.0
                    continue
                self.cache.append((seg_idx, tile_idx, rate))
                time_list.append(curr_time)
                self.current_size += 1
                num_bit_transmitted += rate * Config.tile_ratio
                self.curr_bitsize += rate * Config.tile_ratio

        elif self.cache_method == 17:
            # Do caching based transcoding
            current_case_path = ratio_path + 'duration/'
            ratio_write = open(current_case_path + 'm1_coor' + str(self.coor) + '_opt' + str(self.optimize) + '.txt', 'w')
            next_time = processed_seq[0][0]

            self.cache = dict()
            for t_idx in range(len(processed_seq)):
                if t_idx% int(0.05*n_request_tiles)==0:
                    print(t_idx)
                # Write size and transcoding
                time = processed_seq[t_idx][0]
                if time >= next_time:
                    # Sort and then pop
                    temp_sort = sorted(self.cache.items(), key=lambda x:x[1])
                    while len(temp_sort) and  temp_sort[0][1][0] < time - self.interval:
                        p_tile_rate = temp_sort[0][1][1]
                        self.current_size -= 1
                        self.curr_bitsize -= p_tile_rate * Config.tile_ratio
                        del temp_sort[0]
                    ratio_write.write(str(time/Config.ms_in_s) + ' ' + str(self.curr_bitsize) + ' ' + str(self.current_size) + ' ' + str(num_of_transcoding))
                    ratio_write.write('\n')
                    next_time += self.time_gap
                    # Convert list to dict
                    self.cache = dict()
                    for element in temp_sort:
                        self.cache[element[0]] = element[1]
                tile = processed_seq[t_idx] 
                seg_idx = tile[1][0]
                tile_idx = tile[1][1]
                rate = tile[1][2]
                num_bit_total += rate * Config.tile_ratio
                if (seg_idx, tile_idx) in self.cache:
                    if rate <= self.cache[(seg_idx, tile_idx)][1]:
                        cache_count += 1.0
                        if rate < self.cache[(seg_idx, tile_idx)][1]:
                            num_of_transcoding += 1.0
                        continue
                    else:
                        self.curr_bitsize -= self.cache[(seg_idx, tile_idx)][1] * Config.tile_ratio
                        self.cache[(seg_idx, tile_idx)] = (time, rate)
                        num_bit_transmitted += rate * Config.tile_ratio
                        self.curr_bitsize += rate * Config.tile_ratio
                else:
                    self.cache[(seg_idx, tile_idx)] = (time, rate)
                    self.current_size += 1
                    num_bit_transmitted += rate * Config.tile_ratio
                    self.curr_bitsize += rate * Config.tile_ratio

        elif self.cache_method == 18:
            # Download highest rate from server
            current_case_path = ratio_path + 'duration/'
            ratio_write = open(current_case_path + 'm2_coor' + str(self.coor) + '_opt' + str(self.optimize) + '.txt', 'w')
            next_time = processed_seq[0][0]

            self.cache = dict()
            for t_idx in range(len(processed_seq)):
                if t_idx% int(0.05*n_request_tiles)==0:
                    print(t_idx)
                time = processed_seq[t_idx][0]
                if time >= next_time:
                    # Sort 
                    temp_sort = sorted(self.cache.items(), key=lambda x:x[1])
                    while len(temp_sort) and  temp_sort[0][1][0] < time - self.interval:
                        p_tile_rate = temp_sort[0][1][1]
                        self.current_size -= 1
                        self.curr_bitsize -= p_tile_rate * Config.tile_ratio
                        del temp_sort[0]

                    ratio_write.write(str(time/Config.ms_in_s) + ' ' + str(self.curr_bitsize) + ' ' + str(self.current_size) + ' ' + str(num_of_transcoding))
                    ratio_write.write('\n')
                    next_time += self.time_gap
                    # Convert list to dict
                    self.cache = dict()
                    for element in temp_sort:
                        self.cache[element[0]] = element[1]

                tile = processed_seq[t_idx] 
                seg_idx = tile[1][0]
                tile_idx = tile[1][1]
                rate = tile[1][2]
                num_bit_total += rate * Config.tile_ratio

                if (seg_idx, tile_idx) in self.cache:
                    if rate <= self.cache[(seg_idx, tile_idx)][1]:
                        cache_count += 1.0
                        if rate < self.cache[(seg_idx, tile_idx)][1]:
                            num_of_transcoding += 1.0
                        continue
                    else:
                        print(rate, self.cache[(seg_idx, tile_idx)])
                        assert 0 == 1
                else:
                    self.cache[(seg_idx, tile_idx)] = (time, Config.bitrate[-1])
                    self.current_size += 1
                    num_bit_transmitted += Config.bitrate[-1] * Config.tile_ratio
                    # if rate < Config.bitrate[-1]:
                    #     num_of_transcoding += 1.0
                    self.curr_bitsize += Config.bitrate[-1] * Config.tile_ratio

        elif self.cache_method == 19:
            # Download highest rate for all tiles from server
            current_case_path = ratio_path + 'duration/'
            ratio_write = open(current_case_path + 'm3_coor' + str(self.coor) + '_opt' + str(self.optimize) + '.txt', 'w')
            next_time = processed_seq[0][0]

            self.cache = dict()
            for t_idx in range(len(processed_seq)):
                if t_idx% int(0.05*n_request_tiles)==0:
                    print(t_idx)
                time = processed_seq[t_idx][0]
                if time >= next_time:
                    # Sort 
                    temp_sort = sorted(self.cache.items(), key=lambda x:x[1])
                    while len(temp_sort) and temp_sort[0][1][0] < time - self.interval:
                        p_tile_rate = temp_sort[0][1][1]
                        self.current_size -= Config.n_pitch * Config.n_yaw
                        self.curr_bitsize -= p_tile_rate
                        del temp_sort[0]

                    ratio_write.write(str(time/Config.ms_in_s) + ' ' + str(self.curr_bitsize)+ ' ' + str(self.current_size)  + ' ' + str(num_of_transcoding))
                    ratio_write.write('\n')
                    next_time += self.time_gap
                    # Convert list to dict
                    self.cache = dict()
                    for element in temp_sort:
                        self.cache[element[0]] = element[1]

                tile = processed_seq[t_idx] 
                seg_idx = tile[1][0]
                tile_idx = tile[1][1]
                rate = tile[1][2]
                num_bit_total += rate * Config.tile_ratio

                if seg_idx not in self.cache:
                    # Assume all tiles are cached
                    self.cache[seg_idx] = (time, Config.bitrate[-1])
                    num_bit_transmitted += Config.bitrate[-1]
                    self.current_size += Config.n_yaw * Config.n_pitch
                    self.curr_bitsize += Config.bitrate[-1]

                assert seg_idx in self.cache
                cache_count += 1.0
                if rate < Config.bitrate[-1]:
                    num_of_transcoding += 1.0
        print("Final cache size is: ", self.current_size)
        print("Total cache count: ", cache_count)
        print("Total requested tiles: ", n_request_tiles)
        print("Cache ratio: ", cache_count/n_request_tiles)
        return self.current_size, cache_count, n_request_tiles, cache_count/n_request_tiles, num_bit_total, num_bit_transmitted, num_of_transcoding, self.curr_bitsize

    def load_represent(self):
        repre_list = []
        repre_data_str = 'usrs' + str(N_USERS) + '_coor' + str(self.coor) + '_latency' + str(self.optimize) + '.txt'
        repre_data_path = './represent/user_' + str(N_USERS) + '/'
        with open(repre_data_path + repre_data_str, 'r') as repre_read:
            for line in repre_read:
                time = float(line.strip('\n').split(' ')[0])
                repre = [int(rep) for rep in line.strip('\n').split(' ')[1:]]
                repre_list.append((time, repre))

        not_repre_list = []     
        not_repre_data_str = 'not_usrs' + str(N_USERS) + '_coor' + str(self.coor) + '_latency' + str(self.optimize) + '.txt'
        repre_data_path = './represent/user_' + str(N_USERS) + '/'
        with open(repre_data_path + not_repre_data_str, 'r') as not_repre_read:
            for line in not_repre_read:
                time = float(line.strip('\n').split(' ')[0])
                repre = [int(rep) for rep in line.strip('\n').split(' ')[1:]]
                not_repre_list.append((time, repre))

        global_not_repre_list = []     
        global_not_repre_data_str = 'global_not_usrs' + str(N_USERS) + '_coor' + str(self.coor) + '_latency' + str(self.optimize) + '.txt'
        repre_data_path = './represent/user_' + str(N_USERS) + '/'
        with open(repre_data_path + global_not_repre_data_str, 'r') as global_not_repre_read:
            for line in global_not_repre_read:
                time = float(line.strip('\n').split(' ')[0])
                repre = [int(rep) for rep in line.strip('\n').split(' ')[1:]]
                if len(repre) > NUM_GLOBAL_NOT:
                    repre = repre[-NUM_GLOBAL_NOT:]
                global_not_repre_list.append((time, repre))

        global_not_w_repre_list = []     
        global_not_w_repre_data_str = 'global_not_w_usrs' + str(N_USERS) + '_coor' + str(self.coor) + '_latency' + str(self.optimize) + '.txt'
        repre_data_path = './represent/user_' + str(N_USERS) + '/'
        with open(repre_data_path + global_not_w_repre_data_str, 'r') as global_not_w_repre_read:
            for line in global_not_w_repre_read:
                time = float(line.strip('\n').split(' ')[0])
                repre = [int(rep) for rep in line.strip('\n').split(' ')[1:]]
                if len(repre) > NUM_GLOBAL_NOT:
                    repre = repre[:NUM_GLOBAL_NOT]
                global_not_w_repre_list.append((time, repre))

        return repre_list, not_repre_list, global_not_repre_list, global_not_w_repre_list

    def load_cache_data(self):
        cache_data_str = 'usrs' + str(N_USERS) + '_coor' + str(self.coor) + '_latency' + str(self.optimize)
        cache_data_path = './cache/user_' + str(N_USERS) + '/'

        index_list = []
        for file in os.listdir(cache_data_path):
            if cache_data_str not in file:
                continue
            index_list.append(int(file.split('.')[0].split('_')[-1][5:]))
        index_list.sort()
        # print(index_list)
        self.trace = []
        for index in index_list:
            file_name = cache_data_path + cache_data_str + '_index' + str(index) + '.txt'
            with open(file_name, 'r') as fr:
                for line in fr:
                    line.strip('\n')
                    time = float(line.split(' ')[0])
                    u_id = int(line.split(' ')[-1])
                    seg_idx = int(line.split('(')[1].split(',')[0])
                    tile_idx = (int(line.split('(')[2].split(')')[0].split(',')[0]), int(line.split('(')[2].split(')')[0].split(',')[1]))
                    rate = float(line.split(')')[1].strip(', '))
                    self.trace.append([time, (seg_idx, tile_idx, rate), u_id])

