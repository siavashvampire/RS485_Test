from ctypes import *
from typing import Union

from client import MersadModbusClient

__debug = 0

client = MersadModbusClient(host="192.168.1.238", port=502, auto_open=True, auto_close=False, timeout=3, debug=False)
electrical_substation_id = 1


def convert(s):
    i = int(s, 16)                   # convert from hex to a Python int
    cp = pointer(c_int(i))           # make this into a c integer
    fp = cast(cp, POINTER(c_float))  # cast the int pointer to a float pointer
    return fp.contents.value

def Read_PM2100(rs_485_address: int, device_type: int) -> dict[str, Union[int, float]]:
    client.unit_id(rs_485_address)

    # incoming_data_part1 = client.multiple_register_read("holding", 3000, 17, "FLOAT32")
    incoming_data_part1 = client.multiple_register_read("holding", 2999, 17, "FLOAT32")
    num = incoming_data_part1
    # if not num != num:
    if 1:
        # Todo:bar asas device type nis
        # incoming_data_part2 = client.multiple_register_read("holding", 3036, 21, "FLOAT32")
        # incoming_data_part3 = client.multiple_register_read("holding", 3078, 8, "4Q_FP_PF")
        # incoming_data_part4 = client.multiple_register_read("holding", 3110, 1, "FLOAT32")
        # incoming_data_part5 = client.multiple_register_read("holding", 3194, 1, "FLOAT32")
        # incoming_data_part6 = client.multiple_register_read("holding", 3204, 12, "INT64")
        # incoming_data_part7 = client.multiple_register_read("holding", 3272, 4, "INT64")
        # incoming_data_part8 = client.multiple_register_read("holding", 3304, 12, "INT64")
        # incoming_data_part9 = client.multiple_register_read("holding", 3518, 9, "INT64")

        incoming_data_part2 = client.multiple_register_read("holding", 3035, 21, "FLOAT32")
        incoming_data_part3 = client.multiple_register_read("holding", 3077, 8, "FLOAT32")
        incoming_data_part4 = client.multiple_register_read("holding", 3109, 1, "FLOAT32")
        incoming_data_part5 = client.multiple_register_read("holding", 3193, 1, "FLOAT32")
        incoming_data_part6 = client.multiple_register_read("holding", 3203, 12, "INT64")
        # incoming_data_part6 = client.multiple_register_read("holding", 2699, 12, "FLOAT32")
        incoming_data_part7 = client.multiple_register_read("holding", 3272, 4, "INT64")
        incoming_data_part8 = client.multiple_register_read("holding", 3304, 12, "INT64")
        incoming_data_part9 = client.multiple_register_read("holding", 3518, 9, "INT64")
        try:
            incoming_data = incoming_data_part1 + \
                            incoming_data_part2 + \
                            incoming_data_part3 + \
                            incoming_data_part4 + \
                            incoming_data_part5 + \
                            incoming_data_part6 + \
                            incoming_data_part7 + \
                            incoming_data_part8 + \
                            incoming_data_part9

            # for val in incoming_data:
            #     if val != val:
            #         return {"substation_id": 0}

            dict_data_out = {
                "substation_id": electrical_substation_id,
                "unitId": rs_485_address,
                "Current_A": incoming_data[0],
                "Current_B": incoming_data[1],
                "Current_C": incoming_data[2],
                "Current_N": incoming_data[3],
                "Current_G": incoming_data[4],
                "Current_Avg": incoming_data[5],

                "Current_Unbalance_A": incoming_data[6],
                "Current_Unbalance_B": incoming_data[7],
                "Current_Unbalance_C": incoming_data[8],
                "Current_Unbalance_Worst": incoming_data[9],

                "Voltage_A_B": incoming_data[10],
                "Voltage_B_C": incoming_data[11],
                "Voltage_C_A": incoming_data[12],
                "Voltage_L_L_Avg": incoming_data[13],
                "Voltage_A_N": incoming_data[14],
                "Voltage_B_N": incoming_data[15],
                "Voltage_C_N": incoming_data[16],
                "Voltage_L_N_Avg": incoming_data[17],

                "Voltage_Unbalance_A_B": incoming_data[18],
                "Voltage_Unbalance_B_C": incoming_data[19],
                "Voltage_Unbalance_C_A": incoming_data[20],
                "Voltage_Unbalance_L_L_Worst": incoming_data[21],
                "Voltage_Unbalance_A_N": incoming_data[22],
                "Voltage_Unbalance_B_N": incoming_data[23],
                "Voltage_Unbalance_C_N": incoming_data[24],
                "Voltage_Unbalance_L_N_Worst": incoming_data[25],

                "Active_Power_A": incoming_data[26],
                "Active_Power_B": incoming_data[27],
                "Active_Power_C": incoming_data[28],
                "Active_Power_Total": incoming_data[29],
                "Reactive_Power_A": incoming_data[30],
                "Reactive_Power_B": incoming_data[31],
                "Reactive_Power_C": incoming_data[32],
                "Reactive_Power_Total": incoming_data[33],
                "Apparent_Power_A": incoming_data[34],
                "Apparent_Power_B": incoming_data[35],
                "Apparent_Power_C": incoming_data[36],
                "Apparent_Power_Total": incoming_data[37],

                "Power_Factor_A": incoming_data[38],
                "Power_Factor_B": incoming_data[39],
                "Power_Factor_C": incoming_data[40],
                # "Power_Factor_Total": incoming_data[41],
                "Power_Factor_Total": incoming_data[47],
                "Displacement_Power_Factor_A": incoming_data[42],
                "Displacement_Power_Factor_B": incoming_data[43],
                "Displacement_Power_Factor_C": incoming_data[44],
                "Displacement_Power_Factor_Total": incoming_data[45],

                "Frequency": incoming_data[46],

                # "Power_Factor_Total_IEEE": incoming_data[47],

                "Active_Energy_Delivered_Into_Load": incoming_data[48],
                "Active_Energy_Received_Out_of_Load": incoming_data[49],
                "Active_Energy_Delivered_Pos_Received": incoming_data[50],
                "Active_Energy_Delivered_Neg_Received": incoming_data[51],
                "Reactive_Energy_Delivered": incoming_data[52],
                "Reactive_Energy_Received": incoming_data[53],
                "Reactive_Energy_Delivered_Pos_Received": incoming_data[54],
                "Reactive_Energy_Delivered_Neg_Received": incoming_data[55],
                "Apparent_Energy_Delivered": incoming_data[56],
                "Apparent_Energy_Received": incoming_data[57],
                "Apparent_Energy_Delivered_Pos_Received": incoming_data[58],
                "Apparent_Energy_Delivered_Neg_Received": incoming_data[59],

                "Reactive_Energy_in_Quadrant_I": incoming_data[60],
                "Reactive_Energy_in_Quadrant_II": incoming_data[61],
                "Reactive_Energy_in_Quadrant_III": incoming_data[62],
                "Reactive_Energy_in_Quadrant_IV": incoming_data[63],

                "Active_Energy_Delivered_Into_Load_Permanent": incoming_data[64],
                "Active_Energy_Received_Out_of_Load_Permanent": incoming_data[65],
                "Active_Energy_Delivered_Pos_Received_Permanent": incoming_data[66],
                "Active_Energy_Delivered_Neg_Received_Permanent": incoming_data[67],
                "Reactive_Energy_Delivered_Permanent": incoming_data[68],
                "Reactive_Energy_Received_Permanent": incoming_data[69],
                "Reactive_Energy_Delivered_Pos_Received_Permanent": incoming_data[70],
                "Reactive_Energy_Delivered_Neg_Received_Permanent": incoming_data[71],
                "Apparent_Energy_Delivered_Permanent": incoming_data[72],
                "Apparent_Energy_Received_Permanent": incoming_data[73],
                "Apparent_Energy_Delivered_Pos_Received_Permanent": incoming_data[74],
                "Apparent_Energy_Delivered_Neg_Received_Permanent": incoming_data[75],

                "Active_Energy_Delivered_Phase_A": incoming_data[76],
                "Active_Energy_Delivered_Phase_B": incoming_data[77],
                "Active_Energy_Delivered_Phase_C": incoming_data[78],
                "Reactive_Energy_Delivered_Phase_A": incoming_data[79],
                "Reactive_Energy_Delivered_Phase_B": incoming_data[80],
                "Reactive_Energy_Delivered_Phase_C": incoming_data[81],
                "Apparent_Energy_Delivered_Phase_A": incoming_data[82],
                "Apparent_Energy_Delivered_Phase_B": incoming_data[83],
                "Apparent_Energy_Delivered_Phase_C": incoming_data[84]
            }

            # json_data_out = json.dumps(dict_data_out, indent=2)

            return dict_data_out

        except:
            print("Error in Read Data From PM2100")
            return {"substation_id": -1}
    else:
        return {"substation_id": -1}


q = Read_PM2100(1, 1)

print("Voltage_A_N  :   " + str(q["Voltage_A_N"]))
print("Voltage_B_N  :   " + str(q["Voltage_B_N"]))
print("Voltage_C_N  :   " + str(q["Voltage_C_N"]))

print("Voltage_A_N  :   " + str(convert(q["Voltage_A_N"])))
print("Voltage_B_N  :   " + str(convert(q["Voltage_B_N"])))
print("Voltage_C_N  :   " + str(convert(q["Voltage_C_N"])))
