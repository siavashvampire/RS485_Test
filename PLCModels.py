import threading
import winsound
from datetime import datetime
from queue import Queue
from threading import Thread
from time import sleep
from typing import Callable, Union

from PyQt5.QtGui import QPixmap
from dateutil.relativedelta import relativedelta
from persiantools.jdatetime import JalaliDateTime
from client import MersadModbusClient
from tinydb import TinyDB


def electrical_extract_choose(data: dict[str, Union[int, float]]) -> tuple[int, int]:
    return data['substation_id'], data['unitId']

class GateWay:
    DBid: int
    deleteMark: QPixmap
    checkMark: QPixmap
    ret_num: int
    disc_msg_sent: bool
    Connected: bool
    first_good: bool
    first_bad: bool
    SleepTime: int
    ReadCounter: int
    DataCounter: int
    DPS: int
    RPS: int
    TimeDis: datetime
    DiffTime: relativedelta
    read_data: bool
    MessengerQ: Queue[list[str, int, int, int]]
    line_monitoring_queue: Queue[list[int, int]]
    electrical_substation_queue: Queue[list[tuple[int, int], dict[str, Union[int, float]]]]
    thread_func: Callable[[Callable[[], bool]], None]
    stop_thread: bool
    Port: int
    TestPort: int
    IP: str
    Name: str
    client: MersadModbusClient
    ReadingDataThread: Thread
    electrical_devices: list[Device]
    electrical_substation_id: int
    app_name: str

    def __init__(self, db_id: int = 0, ip: str = "192.168.1.238", port: int = 502, name: str = "", test_port: int = 0,
                 messenger_queue: Queue[list[str, int, int, int]] = None,
                 app_name: str = "ElectricalSubstation_0",
                 line_monitoring_queue: Queue[list[int, int]] = None,
                 electrical_substation_queue: Queue[
                     list[tuple[int, int], dict[str, Union[int, float]]]] = None) -> None:
        from core.theme.pic import Pics

        self.DBid = db_id
        self.deleteMark = Pics.deleteMark
        self.checkMark = Pics.checkMark
        self.Port = port
        self.TestPort = test_port
        self.IP = ip
        self.Name = name
        self.app_name = app_name
        self.ret_num = 0
        self.disc_msg_sent = False
        self.Connected = False
        self.first_good = True
        self.first_bad = True
        self.SleepTime = 0
        self.ReadCounter = 0
        self.DataCounter = 0
        self.DPS = 0
        self.RPS = 0
        self.read_data = False

        self.TimeDis = datetime.now()
        self.DiffTime = relativedelta()

        if messenger_queue is not None:
            self.MessengerQ = messenger_queue

        self.line_monitoring_queue = line_monitoring_queue
        self.electrical_substation_queue = electrical_substation_queue
        self.stop_thread = False

        if db_id:
            self.update()

        # if self.DBid < 5 and UI is not None:
        #     self.PLC_Status_lbl = UI.PLC_Status_lbl[self.DBid - 1]
        #     self.PLC_Counter_lbl = UI.PLC_Counter_lbl[self.DBid - 1]
        #     self.lbl_Test = UI.lbl_Test_Virtual[self.DBid - 1]
        #     self.checkBox_Test = UI.checkBox_Test_Virtual[self.DBid - 1]
        #     self.checkBox_Counter = UI.checkBox_Counter[self.DBid - 1]
        #     self.Name_LE = UI.lineEdit_Name[self.DBid - 1]
        #     self.IP_LE = UI.lineEdit_IP[self.DBid - 1]
        #     self.TestPort_LE = UI.lineEdit_TestPort[self.DBid - 1]
        #
        #     self.Name_LE.setText(str(self.Name))
        #     self.IP_LE.setText(str(self.IP))
        #     self.TestPort_LE.setText(str(self.TestPort))
        # else:
        #     self.PLC_Status_lbl = ""
        #     self.PLC_Counter_lbl = ""
        #     self.lbl_Test = ""
        #     self.checkBox_Test = ""
        #     self.checkBox_Counter = ""
        #     self.Name_LE = ""
        #     self.IP_LE = ""
        #     self.TestPort_LE = ""

    def run_thread(self) -> None:
        self.ReadingDataThread.start()
        Logging.da_log("Init PLC " + self.Name, "PLC " + self.Name + " start")

    def update(self) -> None:
        sea = TinyDB(da_unit_db_path).table(da_unit_table_name).get(doc_id=self.DBid)
        self.Port = 502
        self.TestPort = sea["testPort"]
        self.app_name = sea["app"]
        self.IP = sea["IP"]
        self.Name = sea["label"]

        if self.app_name == "LineMonitoring":
            self.thread_func = self.line_monitoring_read_data_from_plc_thread
        elif "ElectricalSubstation" in self.app_name:
            s = self.app_name.split("_")
            self.app_name = s[0]
            self.electrical_substation_id = int(s[1])
            self.electrical_devices = get_devices_by_substation_id(self.electrical_substation_id)
            self.thread_func = self.electrical_substation_read_data_from_plc_thread

        self.client = MersadModbusClient(host=self.IP, port=self.Port, auto_open=True, auto_close=False,
                                         timeout=modbus_timeout, debug=False,
                                         register_for_counter=register_for_counter,
                                         register_for_data=register_for_data,
                                         register_for_start_read=register_for_start_read,
                                         register_for_end_read=register_for_end_read,
                                         register_for_test=register_for_test)

        self.ReadingDataThread = threading.Thread(target=self.thread_func,
                                                  args=(lambda: self.stop_thread,))

    def disconnect(self) -> None:
        if self.first_bad:
            try:
                winsound.Beep(5000, 100)
                winsound.Beep(4000, 100)
                winsound.Beep(3000, 100)
            except Exception as e:
                pass

            self.Connected = False
            self.first_good = True
            self.first_bad = False
            self.TimeDis = datetime.now()
            # self.PLC_Status_lbl.setPixmap(self.deleteMark)
            # self.PLC_Counter_lbl.setStyleSheet("background-color: red;color: white;")
            # self.checkBox_Test.setEnabled(False)
            # self.checkBox_Test.setChecked(False)
            # self.checkBox_Counter.setEnabled(False)
            # self.checkBox_Counter.setChecked(False)

        # self.PLC_Counter_lbl.setText(str(self.ret_num))
        self.DiffTime = relativedelta(datetime.now(), self.TimeDis)
        if getABSecond(self.DiffTime) > disconnect_alarm_time and (not self.disc_msg_sent):
            self.disc_msg_sent = True
            now1 = JalaliDateTime.to_jalali(self.TimeDis).strftime(send_time_format)

            self.MessengerQ.put([PLCDisconnectBaleText.format(Name=self.Name, Time=now1), -1, -4, 1])
            self.MessengerQ.put([PLCDisconnectBaleText.format(Name=self.Name, Time=now1), -1, -4, 2])
            Logging.da_log("Disconnected", "PLC " + self.Name + " Disconnected")

    def connect(self) -> None:
        if self.first_good:

            try:
                winsound.Beep(3000, 100)
                winsound.Beep(4000, 100)
                winsound.Beep(5000, 100)
            except Exception as e:
                pass
            if self.disc_msg_sent:
                now1 = JalaliDateTime.to_jalali(datetime.now()).strftime(send_time_format)
                self.MessengerQ.put(
                    [PLCConnectBaleText.format(Name=self.Name, DiffTime=getText(self.DiffTime), Time=now1), -1, -4, 1])
                self.MessengerQ.put(
                    [PLCConnectBaleText.format(Name=self.Name, DiffTime=getText(self.DiffTime), Time=now1), -1, -4, 2])
                Logging.da_log("Connected", "PLC " + self.Name + " Connected")

            print("connected to PLC {} after {}".format(self.Name, getText(self.DiffTime)))
            self.ret_num = 0
            # self.PLC_Counter_lbl.setStyleSheet("background-color: rgba(" + GreenColor + ");color: white;")
            # self.PLC_Counter_lbl.setText(str(self.ret_num))
            # self.PLC_Status_lbl.setPixmap(self.checkMark)
            # self.checkBox_Test.setEnabled(True)
            # self.checkBox_Counter.setEnabled(True)

            self.Connected = True
            self.first_bad = True
            self.first_good = False
            self.disc_msg_sent = False

    def test(self, data: int) -> None:
        """
        test DAUnits that is alive or not with make a port on and
        Args:
            data: the amount of time that sensor is on in second
        """
        if self.MessengerQ is not None:
            self.MessengerQ.put([VirtualText.format(Name=self.Name, format=self.TestPort, data=data), -2, -4, 1])
            self.MessengerQ.put([VirtualText.format(Name=self.Name, format=self.TestPort, data=data), -2, -4, 2])
        # self.lbl_Test.setText(str(data))

    def counter(self) -> int:
        return self.client.counter()

    def cal_sleep_time(self) -> None:
        dps = self.DPS * 1.2
        if not (dps * 1.3 > self.RPS > dps):
            if dps >= self.RPS:
                self.SleepTime -= plc_sleep_time_step_down
            else:
                self.SleepTime += plc_sleep_time_step_up
        if self.SleepTime <= plc_time_sleep_min:
            self.SleepTime = plc_time_sleep_min
        if self.SleepTime >= plc_time_sleep_max:
            self.SleepTime = plc_time_sleep_max

        if self.read_data:
            self.SleepTime += time_between_read_from_each_device
            self.read_data = False
        self.SleepTime = round(self.SleepTime, 2)

    def restart_thread(self) -> None:
        if not (self.ReadingDataThread.is_alive()):
            self.stop_thread = False
            self.ReadingDataThread = threading.Thread(target=self.thread_func,
                                                      args=(lambda: self.stop_thread,))
            self.ReadingDataThread.start()
            Logging.da_log("Restart PLC " + self.Name, "PLC " + self.Name + " restart")

    def line_monitoring_read_data_from_plc_thread(self, stop_thread: Callable[[], bool]) -> None:
        sleep(1)
        now_sleep = datetime.now()
        while True:
            if stop_thread():
                Logging.da_log("Reading Data Thread " + self.Name, "PLC " + self.Name + " Stop")
                print("stop gateway " + self.Name)
                break
            sleep(self.SleepTime)
            try:
                # plc_is_open = self.client.is_open()
                plc_is_open = self.client.open()
                if not plc_is_open:
                    self.ReadCounter = 0
                    self.DataCounter = 0
                    self.ret_num += 1
                    print("gateway {name} disconnected! | retry number : {num}".format(name=self.Name,
                                                                                       num=self.ret_num))
                    self.disconnect()

                if plc_is_open:
                    self.ReadCounter += 1
                    if (datetime.now() - now_sleep).seconds >= plc_refresh_time:
                        now_sleep = datetime.now()
                        self.DPS = self.DataCounter
                        self.RPS = self.ReadCounter
                        self.ReadCounter = 0
                        self.DataCounter = 0
                        # if not self.checkBox_Counter.isChecked():
                        #     self.PLC_Counter_lbl.setText(str(self.RPS / PLCRefreshTime))
                        self.cal_sleep_time()
                    data, choose = self.line_monitoring_read_data_from_plc()
                    if data is not None:
                        if data:
                            self.DataCounter += 1
                            self.line_monitoring_queue.put([data, choose])

                    # self.connect()
                    # if self.checkBox_Test.isChecked():
                    #     self.client.test(True)
                    # else:
                    #     self.client.test(False)
                    #
                    # if self.checkBox_Counter.isChecked():
                    #     self.SleepTime = 0
                    #     try:
                    #         self.Counter()
                    #     except:
                    #         pass
            except Exception as e:
                Logging.da_log("send and receive " + str(self.DBid), str(e))
                break

    def line_monitoring_read_data_from_plc(self):
        # Todo:in doros nashode bayad doros she az nazar annotation
        data = self.client.safe_read_data()
        if data:
            choose, data = extract_choose(data)
            if choose == int(self.TestPort):
                self.test(data)
                return 0, None
            return data, choose
        else:
            return 0, None

    def electrical_substation_read_data_from_plc_thread(self, stop_thread: Callable[[], bool]) -> None:
        sleep(1)
        now_sleep = datetime.now()
        while True:
            if stop_thread():
                Logging.da_log("Reading Data Thread " + self.Name, "PLC " + self.Name + " Stop")
                print("stop gateway " + self.Name)
                break

            for i in self.electrical_devices:
                if stop_thread():
                    break
                sleep(self.SleepTime)
                try:
                    # plc_is_open = self.client.is_open()
                    plc_is_open = self.client.open()

                    if not plc_is_open:
                        self.ReadCounter = 0
                        self.DataCounter = 0
                        self.ret_num += 1

                        print("gateway {name} disconnected! | retry number : {num}".format(name=self.Name,
                                                                                           num=self.ret_num))
                        self.disconnect()

                    if plc_is_open:
                        self.ReadCounter += 1
                        if (datetime.now() - now_sleep).seconds >= plc_refresh_time:
                            now_sleep = datetime.now()
                            self.DPS = self.DataCounter
                            self.RPS = self.ReadCounter
                            self.ReadCounter = 0
                            self.DataCounter = 0
                            # if not self.checkBox_Counter.isChecked():
                            #     self.PLC_Counter_lbl.setText(str(self.RPS / PLCRefreshTime))
                            self.cal_sleep_time()

                        if (datetime.now() - i.last_read_time_from_device).seconds >= i.refresh_time:
                            data = self.electrical_substation_data_from_plc(i.unit, i.device_type)

                            if data["substation_id"] != -1:
                                i.last_read_time_from_device = datetime.now()

                            if data["substation_id"] != 0 and data["substation_id"] != -1:
                                self.DataCounter += 1
                                self.read_data = True
                                self.cal_sleep_time()
                                choose = electrical_extract_choose(data)
                                self.electrical_substation_queue.put([choose, data])
                            else:
                                pass
                                # TODO: vaghti k none has gozaresh bede to log
                                # print("data from unit {} is None!".format(i.unit))

                        self.connect()

                except Exception as e:
                    print(e)
                    Logging.da_log("send and receive " + str(self.DBid), str(e))
                    break

