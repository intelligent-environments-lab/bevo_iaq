import datetime
import os
import csv

def data_mgmt(data_a):
    """
    Combines and stores sensors' data locally and remotely to AWS S3 bucket.\n
    return: void
    """

    # Store combined sensor data locally and remotely
    timestamp = datetime.datetime.now()
    scd_data_old = data_a["scd"]
    sps_data_old = data_a["sps"]
    data = [
        {
            "Timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "Temperature [C]": scd_data_old["TC"],
            "Relative Humidity": scd_data_old["RH"],
            "CO2": scd_data_old["CO2"],
            "PM_N_0p5": sps_data_old["pm_n_0p5"],
            "PM_N_1": sps_data_old["pm_n_1"],
            "PM_N_2p5": sps_data_old["pm_n_2p5"],
            "PM_N_4": sps_data_old["pm_n_4"],
            "PM_N_10": sps_data_old["pm_n_10"],
            "PM_C_1": sps_data_old["pm_c_1"],
            "PM_C_2p5": sps_data_old["pm_c_2p5"],
            "PM_C_4": sps_data_old["pm_c_4"],
            "PM_C_10": sps_data_old["pm_c_10"],
        }
    ]

    write_csv2(key="sensirion", date=timestamp, data_header=data[0].keys(), data=data)
    sgp_data_old = data_a['sgp']
    tsl_data_old=data_a['tsl']
    no2_data_old=data_a['dgs_no2']
    co_data_old= data_a['dgs_co']
    data = [{
        'Timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        'TVOC': sgp_data_old['TVOC'],
        'eCO2': sgp_data_old['eCO2'],
        'Lux': tsl_data_old['Lux'],
        'Visible': tsl_data_old['Visible'],
        'Infrared': tsl_data_old['Infrared'],
        'NO2': no2_data_old['NO2'],
        'T_NO2': no2_data_old['T_NO2'],
        'RH_NO2': no2_data_old['RH_NO2'],
        'CO': co_data_old['CO'],
        'T_CO': co_data_old['T_CO'],
        'RH_CO': co_data_old['RH_CO']
    }]
    key = 'adafruit'
    write_csv3(
        key=key,
        date=timestamp,
        data_header=data[0].keys(),
        data=data
    )


def write_csv2(key, date, data_header, data):
    """
    Writes data to csv file. Key is used to decipher the filepath and style of the filename.
    Date filename is used to name & sort files chronologically. Creates a new file if none with
    filename exists or appends to the exsiting file. The data header specifies the field
    names and is a list of the dictionary keys. Data is a list of dictionaries.\n
    key: string\\
    date: datetime.datetime\\
    data_header: list\\
    data: list\\
    return: void
    """
    FILEPATH = {
        'sensirion': '/home/pi/DATA/sensirion/'
    }
    beacon = 'test'
    filename_writer = {
        "sensirion": lambda date: FILEPATH["sensirion"]
        + "b"
        + beacon
        + "_"
        + date.strftime("%Y-%m-%d")
        + ".csv"
    }
    filename = filename_writer[key](date=date)
    try:
        if not os.path.isfile(filename):

            with open(filename, mode="w") as data_file:
                csv_dict_writer = csv.DictWriter(data_file, fieldnames=data_header)
                csv_dict_writer.writeheader()
                csv_dict_writer.writerows(data)
                print("Wrote data for first time to:", filename)
        else:
            # Append to already existing file
            with open(filename, mode="a") as data_file:
                csv_dict_writer = csv.DictWriter(data_file, fieldnames=data_header)
                csv_dict_writer.writerows(data)
                print("Appended data to:", filename)
    except Exception as e:
        print(type(e).__name__ + ": " + str(e))

import traceback

def write_csv3(key, date, data_header, data):
    '''
    Writes data to csv file. Key is used to decipher the filepath and style of the filename.
    Date filename is used to name & sort files chronologically. Creates a new file if none with
    filename exists or appends to the exsiting file. The data header specifies the field
    names and is a list of the dictionary keys. Data is a list of dictionaries.\n
    key: string\\
    date: datetime.datetime\\
    data_header: list\\
    data: list\\
    return: void
    '''
    beacon= '00'
    FILEPATH = {
        'adafruit':'/home/pi/DATA/adafruit/'
    }
    filename_writer = {
        'adafruit': lambda date: FILEPATH['adafruit'] + 'b' + beacon + '_' + date.strftime('%Y-%m-%d') + '.csv'
    }
    filename = filename_writer[key](date=date)
    verbose = True
    try:
        if not os.path.isfile(filename):

            with open(filename, mode='w+') as data_file:
                csv_dict_writer = csv.DictWriter(data_file, fieldnames=data_header)
                csv_dict_writer.writeheader()
                csv_dict_writer.writerows(data)
                if verbose:
                    print('Wrote data for first time to:', filename)
        else:
            # Append to already existing file
            with open(filename, mode='a') as data_file:
                csv_dict_writer = csv.DictWriter(data_file, fieldnames=data_header)
                csv_dict_writer.writerows(data)
                if verbose:
                    print('Appended data to:', filename)
    except Exception as e:
        traceback.format_exc()
        if verbose:
            print(type(e).__name__ + ': ' + str(e))