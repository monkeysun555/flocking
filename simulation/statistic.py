import numpy as np
import utils
from config import Config
from scipy.io import loadmat

def do_statistic():
    video_fovs, v_length = utils.load_fovs_for_video()        # (48, *) fovs for one video
    time_traces, bandwidth_traces = utils.load_bw_traces()

    user_distribution = []
    for i in range(Config.num_users):
        user_fov = video_fovs[i]
        distributions = calculate_distribution_from_trace(user_fov[1:])
        user_distribution.append([i, distributions])

    for i in range(len(user_distribution)):
        user_n_tiles = []
        user_entropy = []
        for seg in user_distribution[i][1]:
            user_n_tiles.append(seg[1])
            user_entropy.append(get_entropy(seg[2]))
        print("User: ", i, " wathes ", np.mean(user_n_tiles), " on average.")
        print("User: ", i, " average entropy ", np.mean(user_entropy))
    # for i in range(len(user_distribution)):
        # 

def get_entropy(tiles):
    tiles = np.clip(tiles, 1e-12, 1. - 1e-12)
    return -np.sum(tiles*np.log(tiles))

def calculate_distribution_from_trace(trace):
    tile_map = loadmat(Config.tile_map_dir)['map']
    distribution_of_trace = []
    for i in range(len(trace)):
        seg_id = trace[i][0]
        ground_tile_distribution = np.zeros((Config.n_pitch, Config.n_yaw))
        frames_info = trace[i][1:]
        n_frames = len(frames_info)
        frame_weight = 1.0/float(n_frames)
        for j in range(len(frames_info)):
            frame_tiles = tile_map[int(frames_info[j][1][1]/np.pi*180+90)][int(frames_info[j][1][0]/np.pi*180+180)]
            ground_tile_distribution += frame_tiles/np.sum(frame_tiles)
        ground_tile_distribution *= frame_weight
        n_watch_tile = len([tile for yaw in ground_tile_distribution for tile in yaw if np.round(tile, 2) > 0])
        distribution_of_trace.append([seg_id, n_watch_tile, ground_tile_distribution])
    # print(distribution_of_trace)
    return distribution_of_trace

def main():
    do_statistic()

if __name__ == '__main__':
    main()