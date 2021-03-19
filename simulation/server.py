import os
import numpy as np
import matplotlib.pyplot as plt
from config import Config
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from utils import *
from scipy.io import loadmat

# Note:
# 1. ratio between I and P is 10~15

class Server(object):
    def __init__(self):
        np.random.seed(Config.randomSeed)
        # Configuration
        self.seg_duration = Config.seg_duration
        self.n_yaw = Config.n_yaw
        self.n_pitch = Config.n_pitch

        # Server encoding state
        self.video_rates = Config.bitrate
        self.encoding_time = Config.initial_latencies[Config.latency_control_version]*Config.seg_duration + np.random.random()*Config.seg_duration
        self.current_seg_idx = 0
        self.encoding_buffer = []
        self.update_encoding_buffer(0.0, self.encoding_time)
        # Server connection state
        self.n_clients = Config.num_users
        # self.client_info = []

        # Server FoV collection
        self.client_fovs = dict()
        self.req_seg_idx_list = dict()
        self.playing_time_list = dict()
        self.fov_count = 0
        self.last_seg_idx = 0
        # for DBSCAN clustering
        # self.scaler = StandardScaler()
        # if Config.transform_sim:
        #     self.dbscan = DBSCAN(eps=Config.dbscan_eps, metric=transform_similarity)
        # else:
        #     self.dbscan = DBSCAN(eps=Config.dbscan_eps, metric=similarity)

        self.tile_map = loadmat(Config.tile_map_dir)['map']
        self.distribution_map = dict()

        self.highest_user_idx = None
        self.lowest_user_idx = None
        self.global_lowest_idx = None

    def update(self, downloadig_time):
        # update time and encoding buffer
        # Has nothing to do with sync, migrate to player side
        # sync = 0  # sync play
        # missing_count = 0
        # new_heading_time = 0.0
        pre_time = self.encoding_time
        self.encoding_time += downloadig_time
        self.update_encoding_buffer(pre_time, self.encoding_time)
        # Generate new delivery for next
        # self.generate_next_delivery()

        # # Check delay threshold
        # # A: Triggered by server sice, not reasonable
        # if len(self.chunks) > 1:
        #   if self.time - playing_time > self.delay_tol:
        #       new_heading_time, missing_count = self.sync_encoding_buffer()
        #       sync = 1

        # # B: Receive time_out from client, and then resync
        # if time_out:
          # assert len(self.chunks) > 1
        #   new_heading_time, missing_count = self.sync_encoding_buffer()
        #   sync = 1
        # return sync, new_heading_time, missing_count
        print("Server current time: ", self.encoding_time)
        return

    def update_encoding_buffer(self, start_time, end_time):
        temp_time = start_time
        while True:
            next_time = (int(temp_time/self.seg_duration) + 1) * self.seg_duration
            if next_time > end_time:
                break
            # Generate chunks and insert to encoding buffer
            temp_time = next_time
            # If it is the first chunk in a seg
            seg_tiles_size = self.generate_chunk_size()
            self.encoding_buffer.append(seg_tiles_size) 
            self.current_seg_idx += 1 

    def generate_chunk_size(self):
        if Config.encoding_allocation_version == 0:
            # Uniform distribution
            ratio_for_each = 1.0/(self.n_yaw*self.n_pitch)
            seg_tiles_size = [self.current_seg_idx]
            for i in range(len(self.video_rates)):
                vidoe_rate = self.video_rates[i]
                tiles_size = []
                for y_idx in range(self.n_yaw):
                    for p_idx in range(self.n_pitch):
                        tiles_size.append(np.random.normal(ratio_for_each, 0.01*ratio_for_each)*self.seg_duration*vidoe_rate)
                seg_tiles_size.append(tiles_size)
            return seg_tiles_size

    def get_current_info(self):
        return self.encoding_time, self.current_seg_idx

    def find_user_tiers(self):
        # Find user tiers for caching
        curr_playing_time_list = []
        tmp_repre_list = []
        not_tmp_repre_list = []
        for key, value in self.playing_time_list.items():
            curr_playing_time_list.append((key, value))
        curr_playing_time_list.sort(key=lambda x:x[1], reverse = True)
        n_first_tier = int(Config.num_users/4)
        #################### Find single repre ####################
        # first_tier_user = [x[0] for x in curr_playing_time_list[:n_first_tier]]
        # rate_for_f_users = [0.0] * n_first_tier
        # for i in range(n_first_tier, len(curr_playing_time_list)):
        #     uid = curr_playing_time_list[i][0]
        #     current_fov_trace = [(point[1][0], point[1][1]) for point in self.client_fovs[uid][0][1]]
        #     current_seg_idx = self.client_fovs[uid][0][0]
        #     distance_trace = []
        #     for first_tier_idx in range(len(first_tier_user)):
        #         f_user_id = first_tier_user[first_tier_idx]
        #         f_user_trace = [(point[1][0], point[1][1]) for point in self.client_fovs[f_user_id][0][1]]
        #         assert self.client_fovs[f_user_id][0][0] == current_seg_idx
        #         distance = calculate_curve_distance(current_fov_trace, f_user_trace)
        #         distance_trace.append((first_tier_idx, distance_trace)) # Using index of usr, not real uid
        #     closest_f_user = min(distance_trace, key=lambda x:x[1])[0]  # Get min index
        #     rate_for_f_users[closest_f_user] += 1.0

        # # Using last seg trace in self.client_fovs to calculate distance
        # highest_user_idx = rate_for_f_users.index(max(rate_for_f_users))
        # self.highest_user_idx = first_tier_user[highest_user_idx]
        ##########################################################################
        for tier_id in range(4):
            repre_id = curr_playing_time_list[tier_id*n_first_tier][0]
            not_repre_id = curr_playing_time_list[(tier_id+1)*n_first_tier-1][0]
            tmp_repre_list.append(repre_id)
            not_tmp_repre_list.append(not_repre_id)
        self.highest_user_idx = tmp_repre_list
        self.lowest_user_idx = not_tmp_repre_list
        self.global_lowest_idx = [x[0] for x in curr_playing_time_list[int(-Config.num_users/6):]]

    def get_represent(self):
        return self.highest_user_idx, self.lowest_user_idx, self.global_lowest_idx

    def delete_fov_table(self):
        for key, value in self.client_fovs.items():
            i = 0
            while i < len(value):
                # print(value[i][0])
                if np.floor(value[i][0]) < self.last_seg_idx:
                    i += 1
                else:
                    # assert np.floor(value[i][0]) == self.last_seg_idx
                    break
            del self.client_fovs[key][:i]

        for key, value in self.distribution_map.items():
            i = 0
            while i < len(value):
                # print(value[i][0])
                if np.floor(value[i][0]) < self.last_seg_idx:
                    i += 1
                else:
                    # assert np.floor(value[i][0]) == self.last_seg_idx
                    break
            del self.distribution_map[key][:i]

        if Config.fov_update_per_upload:
            pass
        # print('after delete')
        # print(last_seg_idx)
        # for i in range(len(self.client_fovs)):
        #     print(self.client_fovs[i])

    def update_saliency_map_per_upload(self, u_id, len_of_update_info):
        # u_id_len = len(self.client_fovs[u_id])
        # for seg_idx in reversed(range(len_of_update_info)):
        #     # For fov for each seg
        #     # Reversed direction
        #     data = [value[u_id_len-seg_idx-1] for key, value in self.client_fovs.items() if len(value) >= u_id_len - seg_idx]
        #     print(len(data))
        pass

    def update_saliency_map_per_interval(self):
        # Method based on the sampling
        # seg_i = 1
        # tmp_saliency_map = []
        # while True:
        #     data = [(key, value[seg_i-1]) for key, value in self.client_fovs.items() if len(value) >= seg_i]   # The if is checking whether fov info for the seg idx is empty
        #     curr_seg_saliency = []
        #     if len(data) >= Config.DBSCAN_tth:
        #         tmp_seg_idx = data[0][1][0]
        #         curr_seg_saliency.append(tmp_seg_idx)
        #         for r_id in range(Config.num_fov_per_seg):
        #             tmp_u_id = [data[i][0] for i in range(len(data))]
        #             tmp_data = [data[i][1][1][r_id] for i in range(len(data))]
        #             # scaled_data = self.scaler.fit_transform(tmp_data)
        #             scaled_data = tmp_data
        #             clusters = self.dbscan.fit_predict(scaled_data)
        #             curr_ckp_clustered_data = np.array((tmp_u_id, tmp_data, clusters)).T.tolist()
        #             if Config.show_cluster:
        #                 plt.scatter([p[0] for p in tmp_data], [p[1] for p in tmp_data], c=clusters, cmap="plasma")
        #                 plt.show()
        #                 input()
        #             curr_seg_saliency.append(curr_ckp_clustered_data)
        #         seg_i += 1
        #         tmp_saliency_map.append(curr_seg_saliency)
        #     else:
        #         # There is no more fov with enough records
        #         # Update saliency map and return
        #         self.saliency_map_list = tmp_saliency_map
        #         return
        
        ## Build up saliency map for a user using fov (for all frames) for one video segment
        seg_i = 1
        while True:
            # Check for all users
            tmp_saliency_maps = []
            user_datas = [(key, value[seg_i-1]) for key, value in self.client_fovs.items() if len(value) >= seg_i]   # The if is checking whether fov info for the seg idx is empty
            # Build up saliency map from centers of frames
            if len(user_datas):
                # user_datas: [uid, [seg_id, [time, (yaw, pitch, roll)], [time, (yaw, pitch, roll)],...[time, ()]]]
                for user_info in user_datas:
                    # For different users
                    u_id = user_info[0]
                    real_seg_idx = user_info[1][0]
                    frames_info = user_info[1][1]
                    # print("frames info: ", frames_info)
                    distribution = self.get_distribution_from_center(frames_info)

                    if u_id in self.distribution_map.keys():
                        self.distribution_map[u_id].append([real_seg_idx, distribution])
                    else:
                        self.distribution_map[u_id] = [[real_seg_idx, distribution]]
                seg_i += 1
            else:
                return

    def get_distribution_from_center(self, frames_info):
        n_frames = float(len(frames_info))
        frame_distribution = np.zeros((Config.n_pitch, Config.n_yaw))
        for f_info in frames_info:
            pitch_center = int(np.round(f_info[1][1]/np.pi*180)) + 90        # Index offset
            yaw_center = int(np.round(f_info[1][0]/np.pi*180)) + 180         # Index offset
            # print(pitch_center, yaw_center)
            tiles = self.tile_map[pitch_center][yaw_center]
            frame_distribution += np.array(tiles)/np.sum(tiles)     # Get total numbers for tiles for one frame, then normalized
        frame_distribution /= n_frames
        return frame_distribution

    def find_tiles(fov_direction):
        yaw = fov_direction[0]
        pitch = fov_direction[1]

    def collect_fov_info(self, u_id, fov_info, req_seg_idx, playing_time, initial=False):
        # print(u_id, req_seg_idx)
        if u_id in self.client_fovs.keys():
            self.client_fovs[u_id].extend(fov_info)
        else:
            self.client_fovs[u_id] = fov_info
        self.req_seg_idx_list[u_id] = req_seg_idx
        self.playing_time_list[u_id] = playing_time
        if not initial:
            self.fov_count += 1
            if self.fov_count%Config.table_delete_interval == 0:
                # print('kllls')
                # for i in range(len(self.client_fovs)):
                #     print(len(self.client_fovs[i]))
                # print(self.req_seg_idx_list)
                # print(self.playing_time_list)
                self.find_user_tiers()

                self.fov_count = 0
                last_user = min(self.playing_time_list, key=self.playing_time_list.get)
                self.last_seg_idx = max(0, int(np.floor(self.playing_time_list[last_user]/Config.seg_duration)) - Config.server_fov_pre_len)
                
                if Config.show_system:
                    print("Last user playing idx is: ", self.last_seg_idx)
                self.delete_fov_table()
                # Only update per interval for all
                self.update_saliency_map_per_interval()

    def get_user_fovs(self, display_segs, seg_idx):
        # Get distribution and history fov traces of other users to the target user
        neighbors_trace = []
        distribution_map = []
        user_dis_maps = dict()
        if Config.fov_debug:
            print("Requested idx: ", seg_idx)
            print("head of trace_idx: ", self.last_seg_idx)
        head_of_trace_idx = self.last_seg_idx
        for key, value in self.distribution_map.items():
            # For each user
            if value[-1][0] >= seg_idx:
                user_display_trace = []
                user_traces = self.client_fovs[key]
                # assert user_traces[0][0] == head_of_trace_idx
                for display_seg in display_segs:
                    if Config.fov_debug:
                        print("User trace seg idx: ", user_traces[display_seg - head_of_trace_idx][0])
                        print("History fov seg idx : ", display_seg)
                    # assert user_traces[display_seg - head_of_trace_idx][0] == display_seg
                    user_display_trace.append(user_traces[display_seg - head_of_trace_idx])
                neighbors_trace.append([key, user_display_trace])
                # Get distribution map
                user_distribution = self.distribution_map[key]
                for dis in user_distribution:
                    if dis[0] == seg_idx:
                        user_dis_maps[key] = (dis[0], dis[1])
        return neighbors_trace, user_dis_maps
