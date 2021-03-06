from __future__ import print_function, absolute_import, division

import os as _os

import numpy as np
import pandas as pd

from mousestyles import data_dir


def load_all_features():
    """
    Returns a (21131, 13) size pandas.DataFrame object corresponding to
    9 features over each mouse's 2-hour time bin. The first four columns
    index each mouses's 2-hour bin:

    Column 0: the strain of the mouse (0-15)
    Column 1: the mouse number (number depends on strain)
    Column 2: the day number (5-16)
    Column 3: the 2-hour time bin (e.g., value 4 corresponds to hours 4 to 6)

    The remaining 9 columns are the computed features.

    Returns
    -------
    features_data_frame : pandas.DataFrame
        A dataframe of computed features.
    """
    features = [
        'ASProbability',
        'ASNumbers',
        'ASDurations',
        'Food',
        'Water',
        'Distance',
        'ASFoodIntensity',
        'ASWaterIntensity',
        'MoveASIntensity']

    # 9 x 1921 x (3 labels + 11 feature time bins)
    all_features = np.load(
        _os.path.join(
            data_dir,
            'all_features_mousedays_11bins.npy'))

    # Here we begin reshaping the 3-d numpy array into a pandas 2-d dataframe
    columns = ['strain', 'mouse', 'day']
    # Append 2-hour time bin values
    columns += list(range(0, 22, 2))

    # For each feature, unpivot its dataframe so that the 2-hour
    # time bins become a value column, rather than a dimension
    data_frames = []
    for (i, feature) in enumerate(features):
        df = pd.DataFrame(data=all_features[i, :, :], columns=columns)
        melted_df = pd.melt(df, id_vars=columns[:3], value_vars=columns[3:],
                            var_name='hour', value_name=feature)
        data_frames.append(melted_df)

    # Connect each of the feature dataframes to make one dataframe
    all_features_df = data_frames.pop(0)
    other_features = [x.iloc[:, -1] for x in data_frames]
    other_features.insert(0, all_features_df)
    return pd.concat(other_features, axis=1)


def load_intervals(feature):
    """
    Return a pandas.DataFrame object of project interval data
    for the specified feature.

    There are 5 columns in the dataframe:
    strain: the strain number of the mouse
    mouse: the mouse number in its strain
    day: the day number
    start: the start time
    stop: the stop time

    Parameters
    ----------
    feature: {"AS", "F", "IS", "M_AS", "M_IS", "W"}

    Returns
    -------
    intervals : pandas.DataFrame
        All data of the specified feature as a dataframe

    Examples
    --------
    >>> AS = load_intervals('AS')
    >>> IS = load_intervals('IS')
    """
    # check input is one of the provided choices
    if feature not in {"AS", "F", "IS", "M_AS", "M_IS", "W"}:
        raise ValueError(
            'Input value must be one of {"AS", "F", "IS", "M_AS", "M_IS", "W"}'
            )
    # get all file names
    file_names = _os.listdir(_os.path.join(data_dir, "intervals", feature))
    # check if directory is empty
    if len(file_names) == 0:
        raise ValueError('Directory is empty; no file found.')
    # initialized data frame
    # use for loop to load every file and concat to overall data frame
    dt = pd.DataFrame()
    for item in file_names:
        strain = int(item.split("strain")[1].split("_mouse")[0])
        mouse = int(item.split("mouse")[1].split("_day")[0])
        day = int(item.split("day")[1].split(".npy")[0])
        path = _os.path.join(data_dir, "intervals", feature, item)
        sub = np.load(path)
        dt_sub = pd.DataFrame()
        dt_sub["strain"] = [strain] * sub.shape[0]
        dt_sub["mouse"] = [mouse] * sub.shape[0]
        dt_sub["day"] = [day] * sub.shape[0]
        dt_sub["start"] = sub[:, 0]
        dt_sub["stop"] = sub[:, 1]
        dt = pd.concat([dt, dt_sub])
    # sort based on strain, mouse and day
    dt = dt.sort(["strain", "mouse", "day"])
    dt.index = range(dt.shape[0])
    return dt


def load_movement(strain, mouse, day):
    """
    Return a pandas.DataFrame object of project movement data
    for the specified combination of strain, mouse and day.

    There are 4 columns in the dataframe:
    t: Time coordinates (in seconds)
    x: X coordinates indicating the left-right position of the cage
    y: Y coordinates indicating the front-back position of the cage
    isHB: Boolean indicating whether the point is in the home base or not

    Parameters
    ----------
    strain: int
        nonnegative integer indicating the strain number
    mouse: int
        nonnegative integer indicating the mouse number
    day: int
        nonnegative integer indicating the day number

    Returns
    -------
    movement : pandas.DataFrame
        CT, CX, CY coordinates and home base status
        of the combination of strain, mouse and day

    Examples
    --------
    >>> movement = load_movement(0, 0, 0)
    >>> movement = load_movement(1, 2, 1)
    """
    # check if all inputs are nonnegative integers
    conditions_value = [strain < 0, mouse < 0, day < 0]
    conditions_type = [type(strain) != int, type(mouse) != int,
                       type(day) != int]
    if any(conditions_value):
        raise ValueError("Input values need to be nonnegative")
    if any(conditions_type):
        raise TypeError("Input values need to be integer")
    # load all four files of HB, CT, CX and CY data
    HB_path = "txy_coords/C_idx_HB/C_idx_HB_strain{}_mouse{}_day{}.npy".\
        format(strain, mouse, day)
    CT_path = "txy_coords/CT/CT_strain{}_mouse{}_day{}.npy".\
        format(strain, mouse, day)
    CX_path = "txy_coords/CX/CX_strain{}_mouse{}_day{}.npy".\
        format(strain, mouse, day)
    CY_path = "txy_coords/CY/CY_strain{}_mouse{}_day{}.npy".\
        format(strain, mouse, day)
    HB = np.load(_os.path.join(data_dir, HB_path))
    CT = np.load(_os.path.join(data_dir, CT_path))
    CX = np.load(_os.path.join(data_dir, CX_path))
    CY = np.load(_os.path.join(data_dir, CY_path))
    # make data frame
    dt = pd.DataFrame()
    dt["t"] = CT
    dt["x"] = CX
    dt["y"] = CY
    dt["isHB"] = HB
    return dt
