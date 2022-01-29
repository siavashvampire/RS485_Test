from ctypes import *
from typing import Union

from client import MersadModbusClient

from pyModbusTCP import utils

__debug = 0

client = MersadModbusClient(host="192.168.1.238", port=502, auto_open=True, auto_close=False, timeout=3, debug=False)
electrical_substation_id = 1


def convert(s):
    i = int(s, 16)  # convert from hex to a Python int
    cp = pointer(c_int(i))  # make this into a c integer
    fp = cast(cp, POINTER(c_float))  # cast the int pointer to a float pointer
    # return i
    return fp.contents.value


def Read_PM2xxx(rs_485_address: int, device_type: int) -> dict[str, Union[int, float]]:
    client.unit_id(rs_485_address)

    incoming_data_part1 = client.multiple_register_read("holding", 2699, 12, "FLOAT32")
    num = incoming_data_part1[0]

    if not num != num:
        # Todo:bar asas device type nis
        incoming_data_part2 = client.multiple_register_read("holding", 2999, 6, "FLOAT32")
        incoming_data_part3 = client.multiple_register_read("holding", 3019, 9, "FLOAT32")
        incoming_data_part4 = client.multiple_register_read("holding", 3053, 20, "FLOAT32")
        incoming_data_part5 = client.multiple_register_read("holding", 3109, 1, "FLOAT32")
        incoming_data_part6 = client.multiple_register_read("holding", 3763, 4, "FLOAT32")
        incoming_data_part6_1 = client.multiple_register_read("holding", 3771, 1, "DATETIME")
        incoming_data_part7 = client.multiple_register_read("holding", 3779, 4, "FLOAT32")
        incoming_data_part7_1 = client.multiple_register_read("holding", 3787, 1, "DATETIME")
        incoming_data_part8 = client.multiple_register_read("holding", 3795, 4, "FLOAT32")
        incoming_data_part8_1 = client.multiple_register_read("holding", 3803, 1, "DATETIME")
        incoming_data_part9 = client.multiple_register_read("holding", 3875, 4, "FLOAT32")
        incoming_data_part10 = client.multiple_register_read("holding", 3883, 1, "DATETIME")

        try:
            incoming_data_part6 = incoming_data_part6 + incoming_data_part6_1
            incoming_data_part7 = incoming_data_part7 + incoming_data_part7_1
            incoming_data_part8 = incoming_data_part8 + incoming_data_part8_1
            incoming_data = incoming_data_part1 + \
                            incoming_data_part2 + \
                            incoming_data_part3 + \
                            incoming_data_part4 + \
                            incoming_data_part5 + \
                            incoming_data_part6 + \
                            incoming_data_part7 + \
                            incoming_data_part8 + \
                            incoming_data_part9 + \
                            incoming_data_part10

            # for val in incoming_data:
            #     if val != val:
            #         return {"substation_id": 0}

            dict_data_out = {
                "substation_id": electrical_substation_id,
                "unitId": rs_485_address,

                "Active_Energy_Delivered": incoming_data[0],
                "Active_Energy_Received": incoming_data[1],
                "Active_Energy_Delivered_Pos_Received": incoming_data[2],
                "Active_Energy_Delivered_Neg_Received": incoming_data[3],
                "Reactive_Energy_Delivered": incoming_data[4],
                "Reactive_Energy_Received": incoming_data[5],
                "Reactive_Energy_Delivered_Pos_Received": incoming_data[6],
                "Reactive_Energy_Delivered_Neg_Received": incoming_data[7],
                "Apparent_Energy_Delivered": incoming_data[8],
                "Apparent_Energy_Received": incoming_data[9],
                "Apparent_Energy_Delivered_Pos_Received": incoming_data[10],
                "Apparent_Energy_Delivered_Neg_Received": incoming_data[11],

                "Current_A": incoming_data[12],
                "Current_B": incoming_data[13],
                "Current_C": incoming_data[14],
                "Current_N": incoming_data[15],
                "Current_G": incoming_data[16],
                "Current_Avg": incoming_data[17],

                "Voltage_A_B": incoming_data[18],
                "Voltage_B_C": incoming_data[19],
                "Voltage_C_A": incoming_data[20],
                "Voltage_L_L_Avg": incoming_data[21],
                "Voltage_A_N": incoming_data[22],
                "Voltage_B_N": incoming_data[23],
                "Voltage_C_N": incoming_data[24],
                "Voltage_L_N_Avg": incoming_data[26],

                "Active_Power_A": incoming_data[27],
                "Active_Power_B": incoming_data[28],
                "Active_Power_C": incoming_data[28],
                "Active_Power_Total": incoming_data[30],
                "Reactive_Power_A": incoming_data[31],
                "Reactive_Power_B": incoming_data[32],
                "Reactive_Power_C": incoming_data[33],
                "Reactive_Power_Total": incoming_data[34],
                "Apparent_Power_A": incoming_data[35],
                "Apparent_Power_B": incoming_data[36],
                "Apparent_Power_C": incoming_data[37],
                "Apparent_Power_Total": incoming_data[38],

                "Power_Factor_A": incoming_data[39],
                "Power_Factor_B": incoming_data[40],
                "Power_Factor_C": incoming_data[41],
                "Power_Factor_Total": incoming_data[42],
                "Displacement_Power_Factor_A": incoming_data[43],
                "Displacement_Power_Factor_B": incoming_data[44],
                "Displacement_Power_Factor_C": incoming_data[45],
                "Displacement_Power_Factor_Total": incoming_data[46],

                "Frequency": incoming_data[47],

                "Active_Power_Last_Demand": incoming_data[48],
                "Active_Power_Present_Demand": incoming_data[49],
                "Active_Power_Predicted_Demand": incoming_data[50],
                "Active_Power_Peak_Demand": incoming_data[51],
                "Active_Power_PK_DT_Demand": incoming_data[52],

                "Reactive_Power_Last_Demand": incoming_data[53],
                "Reactive_Power_Present_Demand": incoming_data[54],
                "Reactive_Power_Predicted_Demand": incoming_data[55],
                "Reactive_Power_Peak_Demand": incoming_data[56],
                "Reactive_Power_PK_DT_Demand": incoming_data[57],

                "Apparent_Power_Last_Demand": incoming_data[58],
                "Apparent_Power_Present_Demand": incoming_data[59],
                "Apparent_Power_Predicted_Demand": incoming_data[60],
                "Apparent_Power_Peak_Demand": incoming_data[61],
                "Apparent_Power_PK_DT_Demand": incoming_data[62],

                "Current_Avg_Last_Demand": incoming_data[63],
                "Current_Avg_Present_Demand": incoming_data[64],
                "Current_Avg_Predicted_Demand": incoming_data[65],
                "Current_Avg_Peak_Demand": incoming_data[66],
                "Current_Avg_PK_DT_Demand": incoming_data[67],
            }

            # json_data_out = json.dumps(dict_data_out, indent=2)

            return dict_data_out

        except Exception as e:
            print(e)
            print("Error in Read Data From PM2100")
            return {"substation_id": -1}
    else:
        return {"substation_id": -1}


q = Read_PM2xxx(2, 1)


# rs_485_address = 1
# client.unit_id(rs_485_address)
# incoming_data_part1 = client.multiple_register_read("holding", 21299, 10, "FLOAT32")
# incoming_data_part2 = client.multiple_register_read("holding", 21321, 16, "FLOAT32")
# incoming_data = incoming_data_part1 + incoming_data_part2
#
# q = {
#     "substation_id": electrical_substation_id,
#     "unitId": rs_485_address,
#
#     "THD_Current_A": incoming_data[0],
#     "THD_Current_B": incoming_data[1],
#     "THD_Current_C": incoming_data[2],
#     "THD_Voltage_A_N": incoming_data[3],
#     "THD_Voltage_B_N": incoming_data[4],
#     "THD_Voltage_C_N": incoming_data[5]
# }

for key, value in q.items():
    print(key, ' : ', value)
