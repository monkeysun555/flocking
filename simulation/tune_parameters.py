import numpy as np
import utils
import random
from config import Config
from scipy.io import loadmat
from multiprocessing import Lock, Process, Manager

P1_LIST = [1, 2, 3, 4, 5]
P2_LIST = [0.5, 1, 1.5, 2, 2.5]

def mp_tune():
    lock = Lock()
    manager = Manager()
    parameters_entropy = manager.list([])
    tuning_path = './tune/tune_results.txt'
    log_file = open(tuning_path, 'w')
    tile_map = loadmat(Config.tile_map_dir)['map']
    processes = []
    video_fovs, v_length = utils.load_fovs_for_video()        # (48, *) fovs for one video
    tune_list = []
    for p1 in P1_LIST:
        for p2 in P2_LIST:
            current_pair = (p1, p2)
            processes.append(Process(target=tune, args=(video_fovs, tile_map, current_pair, parameters_entropy, lock)))
            processes[-1].start()

    for process in processes:
        #   """
        #   Waits for threads to complete before moving on with the main
        #   script.
        #   """
            process.join()

    for pair in parameters_entropy:
        log_file.write("Pair: " +  str(pair[0]) + " entropy: " + str(pair[1]))
        log_file.write('\n')

    # parameters_entropy.sort(key=lambda x:x[1])
    # log_file.write("Best pair is : " + str(parameters_entropy[0][0]) + " entropy: " + str(parameters_entropy[0][1]))
    # log_file.write('\n')

def tune(video_fovs, tile_map, current_pair, parameters_entropy, lock):
    # video_fovs, v_length = utils.load_fovs_for_video()        # (48, *) fovs for one video
    # tune_list = []
    # for p1 in P1_LIST:
    #     for p2 in P2_LIST:
    #         current_pair = (p1, p2)
    #         processes.append(Process(target=find_upper, args=(file_num, buffer_len, curr_dir, t)))
    #         processes[-1].start()
    p1 = current_pair[0]
    p2 = current_pair[1]
    users_info = []
    for u_id in range(Config.num_users):
    # for u_id in range(3):
        print("Current user: ", u_id)
        # For one user, 
        user_fov = video_fovs[u_id][1:]
        user_entropy = []
        for seg_idx in range(20, len(user_fov)):
        # for seg_idx in range(10, 12):
            print("Seg idx: ", seg_idx)
            latency = random.randint(1,4)
            other_distance = []
            f_distribution = np.zeros((Config.n_pitch, Config.n_yaw))
            # Target fov his
            current_past_fov = [(frame[1][0], frame[1][1]) for frame in user_fov[seg_idx-latency][1:]]    # Still in (yaw, pitch)
            
            for other_id in range(Config.num_users):
                if other_id == u_id:
                    continue
                other_trace = [(frame[1][0], frame[1][1]) for frame in video_fovs[other_id][1:][seg_idx-latency][1:]] 
                distance,_ = utils.calculate_curve_distance(current_past_fov, other_trace)
                other_weight = get_weight(p1, p2, distance)

                # Get final distribution
                ground_tile_distribution = np.zeros((Config.n_pitch, Config.n_yaw))
                current_fov = video_fovs[other_id][1:][seg_idx][1:]
                # For other users
                frame_weight = 1.0/float(len(current_fov))
                for frame in current_fov:
                    frame_tiles = tile_map[int(frame[1][1]/np.pi*180+90)][int(frame[1][0]/np.pi*180+180)]
                    ground_tile_distribution += frame_tiles/np.sum(frame_tiles)
                ground_tile_distribution *= frame_weight
                other_distance.append([other_id, distance, other_weight, ground_tile_distribution])

            # Get current user seg_distribution
            c_usr_tile_distribution = np.zeros((Config.n_pitch, Config.n_yaw))
            c_user_fov = user_fov[seg_idx][1:]
            frame_weight = 1.0/float(len(c_user_fov))
            for frame in c_user_fov:
                frame_tiles = tile_map[int(frame[1][1]/np.pi*180+90)][int(frame[1][0]/np.pi*180+180)]
                c_usr_tile_distribution += frame_tiles/np.sum(frame_tiles)
            c_usr_tile_distribution *= frame_weight

            weight_sum = np.sum([user[2] for user in other_distance])
            for user in other_distance:
                f_distribution += (user[2]/weight_sum)*user[3]
            assert np.round(np.sum(f_distribution),2) == 1
            # Get entropy
            kl_divergence = utils.tile_cross_entropy(c_usr_tile_distribution, f_distribution)
            user_entropy.append([seg_idx, kl_divergence])
        users_info.append([u_id, user_entropy])
    ## For all users:
    entropy = 0.0
    for user in users_info:
        entropy += np.mean([x[1] for x in user[1]])
    print("Pair: ", current_pair, " generates entropy ", entropy)
    # log_file.write("Pair: ", current_pair, " generates entropy ", entropy)
    lock.acquire()
    parameters_entropy.append([current_pair, entropy])
    lock.release()

def get_weight(p1, p2, distance):
    return 1 - 1/(1+np.e**(-p1*(distance-p2)))

def main():
    mp_tune()

if __name__ == '__main__':
    main()