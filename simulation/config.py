class Config(object):
    show_system = 0
    debug = 0                   # For debug
    fov_debug = 0               # For fov debug
    bw_debug = 0                # For bw debug
    choose_tile_debug = 0       # For choosing tile debug
    enable_cache = 1

    s_version = 0       # 0 to 2 
    if s_version == 0:
        latency_optimization = 0    # Whether control initial latency based on bandwidth
        coordinate_fov_prediction = 0   # If using joint tile selection or independent
    elif s_version == 1:
        latency_optimization = 0    # Whether control initial latency based on bandwidth
        coordinate_fov_prediction = 1   # If using joint tile selection or independent
    elif s_version == 2:
        latency_optimization = 1    # Whether control initial latency based on bandwidth
        coordinate_fov_prediction = 1   # If using joint tile selection or independent
    
    weight_average = 1              
    represent_update_interval = 5000.0
    show_cluster = 0            # Should DBSCAN clustering
    show_kf = 0                 # Show kalman filter points
    neighbors_show = 0          # Show sililarity of neighbors
    
    video_version = 5           # 0 to 8, different videos
    USE_5G = 1                  # Whether use 5g bw traces
    kf_predict = 0              # Whether use kf to do prediction

    # Different algorithms control
    bw_prediction_method = 1        # 0: mean, 1: Harmonic mean 2, RLS
    neighbors_weight_method = 0     # 
    indep_rate_allocation_method = 1      # (only happen in independent case) 0: equally assign
    joint_rate_allocation_method = 0    

    num_users = 48                   # Number of users 
    randomSeed = 10              
    tsinghua_fov_data_path = '../../Formated_Data/Experiment_2/'
    pickle_root_path = '../pickled_data/'
    figure_path = './figures/user_' + str(num_users) + '/'
    download_seq_path = './cache/user_' + str(num_users) + '/'
    info_data_path = './data/user_' + str(num_users) + '/'
    if USE_5G:
        ori_bw_trace_path = '../new_mix_format_sample/'
        bw_trace_path = '../filtered_data/'
    else:
        bw_trace_path = '../bw_traces/'
    tile_map_dir = '../tile_map/fov_map.mat'
    qr_map_dir = '../tile_map/qr.mat'

    if enable_cache:
        represent_file_path = './represent/user_' + str(num_users) + '/'

    # Configuration
    ms_in_s = 1000.0
    num_fov_per_seg = 3
    transform_sim = 0               # Whether adjsut yaw distance and pitch distance for dbscan epsilon
    DBSCAN_tth = 3
    dbscan_eps = 0.5
    server_fov_pre_len = 3
    predict_tth_len = 15            # At leat 15 fraces needed to predict/truncate
    zero_prediction_tth = 15
    trun_regression_order = 1
    distance_tth = 25               # At most 30 frame
    neighbor_dis_tth = 30           # Threshold of distance to define close neighbor, here 50 degree
    neighbors_upperbound = 3        # At most use 5 closest neighbors

    # Server configuration
    seg_duration = 1000.0
    n_yaw = 6               # 360/6
    n_pitch = 5             # 180/5
    tile_ratio = 1.0/(n_yaw*n_pitch)
    initial_latencies = [10.0, 20.0]    # 10s/20s, corresponding with latencies [-1]
    encoding_allocation_version = 0
    fov_update_per_upload = 0           # Whehter update saliency map per upload
    table_delete_interval = 10          # How frequently update saliency map
    bw_his_len = 10
    coordinate_fov_tth = 5

    # Parameters
    p1 = 3.0
    p2 = 0.5
    alpha = 0.15
    
    # Client configuration
    if USE_5G:
        bitrate = [100.0, 500.0, 1000.0, 1500.0, 2000.0, 2500.0]
        default_rates = [1000.0, 1000.0, 1000.0, 1000.0, 1000.0, 1000.0]
        default_rates_v1 = [1000.0, 1000.0, 1000.0, 1000.0, 1000.0, 1000.0, 1000.0, 1000.0]
    else:
        bitrate = [3.0, 5.0, 8.0, 10.0, 15.0, 20.0]
        default_rates = [20.0, 20.0, 20.0, 20.0, 20.0, 20.0]
        default_rates_v1 = [20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0]

    latency_control_version = 1
    latencies = [[[0.2, 0.3, 0.3, 0.1], [2, 4, 6, 8]],
                 [[0.1, 0.4, 0.4, 0.1], [3, 8, 13, 19]]]
    rtt_low = 10.0
    rtt_high = 20.0 
    packet_payload_portion = 0.98
    freezing_tol = 3000.0   
    user_start_up_th = 2000.0
    default_tiles = [[(1,2), 1], [(1,3), 1],
                     [(2,2), 1], [(2,3), 1],
                     [(3,2), 1], [(3,3), 1]]
    default_tiles_v1 = [[(1,2), 1], [(1,3), 1],
                        [(2,2), 1], [(2,3), 1],
                        [(3,2), 1], [(3,3), 1],
                        [(4,2), 0], [(4,3), 0]]
    user_buffer_upper = 3000.0

    bw_traces_group = [set([105, 102, 95, 73, 177, 125, 167, 82, 198, 190, 134, 101]),
                       set([182, 41, 60, 90, 178, 15, 65, 13, 0, 37, 120, 196]), 
                       set([67, 112, 128, 175, 22, 96, 151, 5, 159, 148, 161, 166]), 
                       set([10, 76, 163, 185, 63, 12, 138, 88, 83, 149, 53, 110])]
