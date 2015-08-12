import serial
import threading

DEFAULT_BAUTRATE = 115200

# V-Sido CONNECTのためのclass
class Connect(object):

    # V-Sidoで利用するコマンドやオペランドのクラス変数定義
    COMMAND_ST = 0xff;
    COMMAND_OP_ANGLE = 0x6f; # 'o'
    COMMAND_OP_IK = 0x6b; # 'k'
    COMMAND_OP_WALK = 0x74; # 't'
    COMMAND_OP_SETVID = 0x73; # 's'
    COMMAND_OP_GPIO = 0x69; # 'i'
    COMMAND_OP_PWM = 0x70; # 'p'

    def __init__(self):
        self.receive_buffer = []

    def connect(self, port, baudrate=DEFAULT_BAUTRATE):
        ''' connect to V-Sido CONNECT RC via serial port '''
        try:
            self.serial = serial.serial_for_url(port, baudrate, timeout=1)
        except serial.SerialException:
            sys.stderr.write("could not open port %r: %s\n" % (port, e))
            raise
        self._start_receiver()

    def disconnect(self):
        ''' disconnect to V-Sido CONNECT RC via serial port '''
        self._stop_receiver()
        self.serial.close()

    def _start_receiver(self):
        """ start receiver thread """
        self.receiver_alive = True
        self.receiver_thread = threading.Thread(target=self._receiver)
        self.receiver_thread.setDaemon(True)
        self.receiver_thread.start()

    def _stop_receiver(self):
        """ start receiver thread """
        self.receiver_alive = False
        self.receiver_thread.join()

    def _receiver(self):
        """ Receiving data """
        try:
            while self.receiver_alive:
                data = self.serial.read(1)
                if len(data) > 0:
                    if data == 0xff:
                        self.receive_buffer = []
                    self.receive_buffer.append(int.from_bytes(data, byteorder='big'))
                    if len(self.receive_buffer) > 3:
                        if len(self.receive_buffer) == self.receive_buffer[2]:
                            receive_buffer_str = []
                            for data in self.receive_buffer:
                                receive_buffer_str.append('%02x' % data)
                            print('< ' + ' '.join(receive_buffer_str))
                            self.receive_buffer = []
        except serial.SerialException:
            self.alive = False
            raise

    def set_servo_angle(self, angle_data_set, cycle_time):
        ''' V-Sido CONNECT "Set_ServoAngle" command '''
        if not isinstance(angle_data_set, list):
            raise ConnectParameterError('set_servo_angle')
            return
        for angle_data in angle_data_set:
            if 'sid' in angle_data:
                if isinstance(angle_data['sid'], int):
                    if angle_data['sid'] < 0 or angle_data['sid'] > 254:
                        raise ConnectParameterError('set_servo_angle')
                        return
            else:
                raise ConnectParameterError('set_servo_angle')
                return
            if 'angle' in angle_data:
                if isinstance(angle_data['angle'], int) or isinstance(angle_data['angle'], float):
                    if angle_data['angle'] < -180.0 or angle_data['angle'] > 180.0:
                        raise ConnectParameterError('set_servo_angle')
                        return
            else:
                raise ConnectParameterError('set_servo_angle')
                return
        if isinstance(cycle_time, int):
            if cycle_time < 0 or cycle_time > 1000:
                raise ConnectParameterError('set_servo_angle')
                return
        else:
            raise ConnectParameterError('set_servo_angle')
            return
        self._send_data(self._make_set_servo_angle_command(angle_data_set, cycle_time))

    def _make_set_servo_angle_command(self, angle_data_set, cycle_time):
        ''' Genarate "Walk" command data '''
        data = []
        data.append(Connect.COMMAND_ST) # ST
        data.append(Connect.COMMAND_OP_ANGLE) # OP
        data.append(0x00) # LN仮置き
        data.append(round(cycle_time / 10)) # CYC(引数はmsec単位で来るが、データは10msec単位で送る)
        for angle_data in angle_data_set:
            data.append(angle_data['sid']) # SID
            angle_data = self._make_2byte_data(round(angle_data['angle'] * 10))
            data.append(angle_data[0]) # ANGLE
            data.append(angle_data[1]) # ANGLE
        data.append(0x00) # SUM仮置き
        return self._adjust_ln_sum(data);

    def set_ik(self, ik_data_set, feedback=False):
        ''' V-Sido CONNECT "Set_ServoAngle" command '''
        if not isinstance(ik_data_set, list):
            raise ConnectParameterError('set_ik')
            return
        for ik_data in ik_data_set:
            if 'kid' in ik_data:
                if isinstance(ik_data['kid'], int):
                    if ik_data['kid'] < 0 or ik_data['kid'] > 254:
                        raise ConnectParameterError('set_ik')
                        return
            else:
                raise ConnectParameterError('set_ik')
                return
            if 'kdt' in ik_data:
                if isinstance(ik_data['kdt'], dict):
                    if 'x' in ik_data['kdt']:
                        if isinstance(ik_data['kdt']['x'], int):
                            if ik_data['kdt']['x'] < -180 or ik_data['kdt']['x'] > 180:
                                raise ConnectParameterError('set_ik')
                                return
                        else:
                            raise ConnectParameterError('set_ik')
                            return
                    else:
                        raise ConnectParameterError('set_ik')
                    if 'y' in ik_data['kdt']:
                        if isinstance(ik_data['kdt']['y'], int):
                            if ik_data['kdt']['y'] < -180 or ik_data['kdt']['y'] > 180:
                                raise ConnectParameterError('set_ik')
                                return
                        else:
                            raise ConnectParameterError('set_ik')
                            return
                    else:
                        raise ConnectParameterError('set_ik')
                        return
                    if 'z' in ik_data['kdt']:
                        if isinstance(ik_data['kdt']['z'], int):
                            if ik_data['kdt']['z'] < -180 or ik_data['kdt']['z'] > 180:
                                raise ConnectParameterError('set_ik')
                                return
                        else:
                            raise ConnectParameterError('set_ik')
                            return
                    else:
                        raise ConnectParameterError('set_ik')
                        return
                else:
                    raise ConnectParameterError('set_ik')
                    return
            else:
                raise ConnectParameterError('set_servo_angle')
                return
        if not isinstance(feedback, bool):
            raise ConnectParameterError('set_ik')
            return
        self._send_data(self._make_set_ik_command(ik_data_set, feedback))

    def _make_set_ik_command(self, ik_data_set, feedback):
        ''' Genarate "set_ik" command data '''
        data = []
        data.append(Connect.COMMAND_ST) # ST
        data.append(Connect.COMMAND_OP_IK) # OP
        data.append(0x00) # LN仮置き
        if not feedback:
            data.append(0x01) # IKF
        else:
            data.append(0x09) # IKF
        for ik_data in ik_data_set:
            data.append(ik_data['kid']) # KID
            data.append(ik_data['kdt']['x'] + 100) # KDT_X
            data.append(ik_data['kdt']['y'] + 100) # KDT_Y
            data.append(ik_data['kdt']['z'] + 100) # KDT_Z
        data.append(0x00) # SUM仮置き
        return self._adjust_ln_sum(data);

    def walk(self, forward, turn_cw):
        ''' V-Sido CONNECT "Walk" command '''
        if isinstance(forward, int):
            if forward < -100 or forward > 100:
                raise ConnectParameterError('walk')
                return
        else:
            raise ConnectParameterError('walk')
            return
        if isinstance(turn_cw, int):
            if turn_cw < -100 or turn_cw > 100:
                raise ConnectParameterError('walk')
                return
        else:
            raise ConnectParameterError('walk')
            return
        self._send_data(self._make_walk_command(forward, turn_cw))

    def _make_walk_command(self, forward, turn_cw):
        ''' Genarate "Walk" command data '''
        data = []
        data.append(Connect.COMMAND_ST) # ST
        data.append(Connect.COMMAND_OP_WALK) # OP
        data.append(0x00) # LN仮置き
        data.append(0x00) # WAD(Utilityでは0で固定)
        data.append(0x02) # WLN(現在2で固定)
        # 速度ならびに旋回は-100〜100を0〜200に変換する
        data.append(forward + 100)
        data.append(turn_cw + 100)
        data.append(0x00) # SUM仮置き
        return self._adjust_ln_sum(data);

    def _send_data(self, command_data):
        ''' Send data to V-Sido CONNECT via serial port '''
        data_bytes = b''
        data_str = []
        for data in command_data:
            data_bytes += data.to_bytes(1, byteorder='little')
            data_str.append('%02x' % data)
        self.serial.write(data_bytes)

        print('> ' + ' '.join(data_str))

    def _make_2byte_data(self, value):
        ''' 2Byte data (see "V-Sido CONNECT RC Command Reference") '''
        value_bytes = value.to_bytes(2, byteorder='big', signed=True)
        return [(value_bytes[1] << 1) & 0x00ff, (value_bytes[0] << 2) & 0x00ff]

    def _adjust_ln_sum(self, command_data):
        ''' adjust LN(Length) & SUM(CheckSum) in command data '''
        #
        ln_pos = 1 if command_data[0] == 0x0c or command_data[0] == 0x0d or command_data[0] == 0x53 or command_data[0] == 0x54 else 2
        if len(command_data) > 3:
            command_data[ln_pos] = len(command_data);
            sum = 0;
            for data in command_data:
                sum ^= data
            command_data[len(command_data) - 1] = sum
            return command_data


class ConnectParameterError(Exception):
    ''' V-Sido CONNECT Command Parameter Error '''
    pass


if __name__ == '__main__':

    import sys
    import time

    DEFAULT_PORT = '/dev/tty.usbserial'

    print("=== Python V-Sido TEST ===")

    # 引数からシリアルポートを決定する
    if len(sys.argv) == 1:
        port = DEFAULT_PORT
    else:
        port = sys.argv[1]
    baudrate = DEFAULT_BAUTRATE

    # V-Sido CONNECT用のインスタンス生成（初期化でシリアルポートをオープンする）
    vsidoconnect = Connect()
    # シリアルポートをオープン、受信スレッドの立ち上げ
    print("Connecting to robot...", end="")
    try:
        vsidoconnect.connect(port, baudrate)
    except serial.SerialException:
        print("fail.")
        sys.exit(1)
    print("done.")
    print("exit: Ctrl-C")
    print("")

    # テストで歩行コマンド
    vsidoconnect.walk(100, 0)
    while True:
        time.sleep(1)