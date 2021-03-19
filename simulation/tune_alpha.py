import numpy as np
import utils
import random
from config import Config
from scipy.io import loadmat
from multiprocessing import Lock, Process, Manager


# 3, 0.5 is the one with smallest cross entropy

ALPHA_LIST = [0.1, 0.3, 0.5, 0.7, 0.9]
P1 = 3.0
P2 = 0.5

def mp_tune():
    lock = Lock()
    manager = Manager()
    parameters_entropy = manager.list([])
    tuning_path = './tune/tune_alpha.txt'
    log_file = open(tuning_path, 'w')
    tile_map = loadmat(Config.tile_map_dir)['map']
    processes = []
    video_fovs, v_length = utils.load_fovs_for_video()        # (48, *) fovs for one video
    tune_list = []
    for alpha in ALPHA_LIST:
        processes.append(Process(target=tune, args=(video_fovs, tile_map, alpha, parameters_entropy, lock)))
        processes[-1].start()

    for process in processes:
        #   """
        #   Waits for threads to complete before moving on with the main
        #   script.
        #   """
            process.join()

    for alpha in parameters_entropy:
        log_file.write("Alpha: " +  str(alpha[0]) + " entropy: " + str(alpha[1]))
        log_file.write('\n')

def prepare_fov_trace(prepared_seg_trace):
    curr_time = [frame_fov[0] for frame_fov in prepared_seg_trace]
    curr_seg_yaw = [frame_fov[1][0]/np.pi*180.0+180 for frame_fov in prepared_seg_trace]
    curr_seg_pitch = [frame_fov[1][1]/np.pi*180.0+90 for frame_fov in prepared_seg_trace]
    processed_curr_seg_yaw = process_degree(curr_seg_yaw)
    return curr_time, processed_curr_seg_yaw, curr_seg_yaw, curr_seg_pitch

def process_degree(trace):
    # print(trace)
    new_trace = [trace[0]]
    for value in trace[1:]:
        if np.abs(value - new_trace[-1]) > 180.0:
            if value < new_trace[-1]:
                new_trace.append(value+360.0)
            elif value > new_trace[-1]:
                new_trace.append(value-360.0)
        else:
            new_trace.append(value)
    return new_trace

def tune(video_fovs, tile_map, alpha, parameters_entropy, lock):
    kf = utils.kalman_filter()
    users_info = []
    for u_id in range(Config.num_users):
    # for u_id in range(3):
        print("Current user: ", u_id)
        # For one user, 
        user_fov = video_fovs[u_id][1:]
        user_entropy = []
        for seg_idx in range(30, len(user_fov)):
        # for seg_idx in range(10, 12):
            print("Seg idx: ", seg_idx)
            latency = random.randint(1,3)
            other_distance = []
            # Target fov his
            current_frams_info = user_fov[seg_idx-latency][1:]
            current_past_fov = [(frame[1][0], frame[1][1]) for frame in user_fov[seg_idx-latency][1:]]    # Still in (yaw, pitch)
            
            # Do prediction
            time_trace, processed_yaw_trace, yaw_trace, pitch_trace = prepare_fov_trace(current_frams_info)
            prediction_gap = latency
            gap = prediction_gap+0.5

            kf.set_traces(time_trace, processed_yaw_trace, pitch_trace)
            kf.init_kf()
            modified_Xs = kf.kf_run(gap)
            if len(modified_Xs) < 2:
                continue
            predicted_center = utils.truncated_linear(gap, time_trace, modified_Xs)
            target_tile_distribution = np.array(tile_map[int(predicted_center[1])][int(predicted_center[0])])
            target_tile_distribution /= np.sum(target_tile_distribution)

            # Get others distribution
            for other_id in range(Config.num_users):
                if other_id == u_id:
                    continue
                other_trace = [(frame[1][0], frame[1][1]) for frame in video_fovs[other_id][1:][seg_idx-latency][1:]] 
                distance,_ = utils.calculate_curve_distance(current_past_fov, other_trace)
                other_weight = get_weight(distance)

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

            other_distribution = np.zeros((Config.n_pitch, Config.n_yaw))
            weight_sum = np.sum([user[2] for user in other_distance])
            for user in other_distance:
                other_distribution += (user[2]/weight_sum)*user[3]
            # assert np.round(np.sum(other_distribution),2) == 1

            # Combine distributions using alpha
            f_distribution = alpha*target_tile_distribution + (1-alpha)*other_distribution
            # assert np.round(np.sum(f_distribution),2) == 1

            # Get current user seg_distribution ground truth
            c_usr_tile_distribution = np.zeros((Config.n_pitch, Config.n_yaw))
            c_user_fov = user_fov[seg_idx][1:]
            frame_weight = 1.0/float(len(c_user_fov))
            for frame in c_user_fov:
                frame_tiles = tile_map[int(frame[1][1]/np.pi*180+90)][int(frame[1][0]/np.pi*180+180)]
                c_usr_tile_distribution += frame_tiles/np.sum(frame_tiles)
            c_usr_tile_distribution *= frame_weight

            kl_divergence = utils.tile_cross_entropy(c_usr_tile_distribution, f_distribution)
            user_entropy.append([seg_idx, kl_divergence])
        users_info.append([u_id, user_entropy])
    ## For all users:
    entropy = 0.0
    for user in users_info:
        entropy += np.mean([x[1] for x in user[1]])
    print("Alpha: ", alpha, " generates entropy ", entropy)
    lock.acquire()
    parameters_entropy.append([alpha, entropy])
    lock.release()

def get_weight(distance):
    return 1 - 1/(1+np.e**(-P1*(distance-P2)))

def main():
    mp_tune()

if __name__ == '__main__':
    main()