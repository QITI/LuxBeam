import socket
import time
import ipaddress
import numpy as np
from .constants import *

__all__ = ["Luxbeam", "LuxbeamError"]

_luxbeam_error_code = {
    10000: "Invalid inum size",
    10001: "Invalid image type",
    10002: "Sequence file package out of order",
    10003: "Error when parsing loaded sequence file. Log can be fetched with4.3.4 Sequencer File Error Log.",
    10004: "Too many sequence file packages (must be <= 20)",
    10005: "Unknown record id (rec_id) received",
    10006: "Invalid sequence command",
    10007: "Mask file package out of order",
    10008: "Too many mask file packages (must be <= 30)",
    10009: "Accessing invalid FPGA register. [Internal]",
    10010: "Translated sequence file is too large",
    10011: "No contact with LED driver or accessing invalid LED driver register. [Internal]",
    10012: "Trying to set an invalid sequence register. Ref 4.3.8 Sequencer Register.",
    10013: "Focus motor number of steps out of range.",
    10014: "Focus motor is busy or in a mode where command cannot be performed.",
    10015: "Focus motor measured distance out of range.",
    10016: "Focus motor CCD thickness out of range.",
    10017: "Focus motor absolute position out of range.",
    10018: "Focus motor has not been set to mid position.",
    10019: "Focus motor measured distance never entered",
    10020: "Mask file with invalifd format (not bmp, not 8-bit, etc)",
    10021: "LED driver amplitude value out of range.",
    10022: "Temperature regulation setvalue out of range.",
    10023: "Focus motor step size conversion unit out of range",
    10024: "Internal sync pulse period outside valid range",
    10025: "AF trim value is outside valid range",
    10026: "AF work range is outside valid range.",
    10027: "AF time delay value is outside valid range.",
    10028: "AF calibration set-position is outside valid range.",
    10029: "AF pull-in range acceleration limit is outside valid range.",
    10030: "AF speed high threshold is outside valid range.",
    10031: "Laser intensity level is outside valid range.",
    10032: "Trig delay outside valid range.",
    10033: "Active Area Qualifier Keepout parameters are outside valid range.",
    10034: "Active Area Qualifier Keepout parameters adds up to a larger number than the active number of pulses.",
    10035: "Trig divide factor outside valid range.",
    10036: "<Currently unused>",
    10037: "OCP limit is out of range.",
    10038: "Strip number out of range.",
    10039: "Internal image number out of range or perrmanent storage error.",
    10040: "Not possible to load sequence file. No file has has been loaded previously.",
    10041: "Invalid fan number",
    10042: "Absolute Z position for AF is outside valid range",
    10043: "Invalid morph record",
    10044: "Led driver firmware package out of order",
    10045: "Led driver firmware crc error",
    10046: "Led driver firmware verification failed",
    10047: "Led driver firmware upgrade ok",
    10048: "Invalid address",
    10049: "Invalid data",
    10050: "Command not supported by old led driver fw"
}


class LuxbeamError(Exception):
    def __init__(self, error_code):
        error_message = "[{0}]: {1}".format(str(error_code), _luxbeam_error_code[error_code])
        super(LuxbeamError, self).__init__(error_message)
        self.error_code = error_code


class Luxbeam(object):
    """

    Parameters
    ----------
    dmd_ip: str
        The IP address of the Luxbeam.
    inverse: bool
    timeout: None or float
        If specify this number will be used for setting the timeout of the socket while communicating with the Luxbeam.
    jumbo_frame: bool

    """
    def __init__(self, dmd_ip, inverse=False, timeout=None, jumbo_frame=False):
        self.UDP_PORT_MAIN = 52985
        self.UDP_PORT_DATA = 52986
        self.DMD_IP = dmd_ip
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        if timeout:
            self.socket.settimeout(timeout)

        self.inverse = inverse
        self.jumbo_frame = jumbo_frame

        dmd_type, blocks, cols, rows, rows_pr_block = self.get_dmd_info()

        if dmd_type not in (DMD_TYPE_1080P_A, DMD_TYPE_XGA_A, DMD_TYPE_XGA_X, DMD_TYPE_WUXGA_A):
            raise EnvironmentError("Unavailable DMD type code: {0}".format(dmd_type))

        self._dmd_type = dmd_type
        self._cols = cols
        self._rows = rows

    @property
    def cols(self):
        return self._cols

    @property
    def rows(self):
        return self._rows

    def recv_ack(self):
        """Receive the ack message from DMD. If the error_code is not zero, raise LuxbeamError.
        Raises
        ------
        :obj:`Luxbeam.luxbeam.LuxbeamError`
        """
        rec_id, payload = self.recv_packet()
        if rec_id == 501:
            error_code = int.from_bytes(payload, byteorder='big')
            if error_code != 0:
                raise LuxbeamError(error_code)

    def send_packet(self, rec_id, payload=None):
        """

        Parameters
        ----------
        rec_id: int
        payload: bytes
        -------
        """
        tot_size = 4
        if payload:
            tot_size += len(payload)
        message = tot_size.to_bytes(2, byteorder='big') + rec_id.to_bytes(2, byteorder='big')
        if payload:
            message = message + payload
        self.socket.sendto(message, (self.DMD_IP, self.UDP_PORT_MAIN))

    def recv_packet(self):
        """Receive the packet from the Luxbeam.

        Returns
        -------
        rec_id: int
        payload: bytes
        """

        data, address = self.socket.recvfrom(1024)
        tot_size = int.from_bytes(data[0:2], byteorder='big')
        rec_id = int.from_bytes(data[2:4], byteorder='big')
        payload = data[4:] if tot_size > 4 else None
        return rec_id, payload

    def get_dmd_info(self):
        """Get various information about the DMD mounted in the Luxbeam.

        Returns
        -------
        dmd_type: int
            The DMD type mounted on the board. See table below for valid values.
            DMD_TYPE_1080P_A: .95 1080p Type A
            DMD_TYPE_XGA_A: .7 XGA Type A
            DMD_TYPE_XGA_X: .55 XGA Type X
            DMD_TYPE_WUXGA_A: .96 WUXGA Type A
            DMD_TYPE_UNKNOWN: Unknown DMD connected. (blocks, cols, etc not valid in this case)
            DMD_TYPE_NO_DMD_CONNECTED: No DMD connected. (blocks, cols, etc not valid in this case)
        blocks: int
            The number of blocks that the DMD is divided into.
        cols: int
            The horizontal pixel resolution of the DMD.
        rows: int
            The vertical pixel resolution for the DMD.
        rows_pr_block: int
            The number of rows in a block.

        """
        self.send_packet(315)
        rec_id, payload = self.recv_packet()
        assert rec_id == 515
        dmd_type = int.from_bytes(payload[0:2], byteorder='big')
        blocks = int.from_bytes(payload[2:4], byteorder='big')
        cols = int.from_bytes(payload[4:6], byteorder='big')
        rows = int.from_bytes(payload[6:8], byteorder='big')
        rows_pr_block = int.from_bytes(payload[8:10], byteorder='big')
        return dmd_type, blocks, cols, rows, rows_pr_block

    def _send_image_packets(self, start_seq_no, end_seq_no, inum, image, img_data_line_num, delay=None):
        """

        Parameters
        ----------
        start_seq_no: int
        end_seq_no: int
        inum: int
        image: bytes
        delay : float
        Returns
        -------
        """
        message_size = (1454).to_bytes(2, byteorder='big')
        message_id = (104).to_bytes(2, byteorder='big')
        m_inum = (inum).to_bytes(4, byteorder='big')

        img_data_byte_num = img_data_line_num * 240

        for i in range(start_seq_no, end_seq_no + 1):
            seq_no = (i).to_bytes(2, byteorder='big')
            offset = (img_data_line_num * (i - 1)).to_bytes(4, byteorder='big')
            bits = image[img_data_byte_num * (i - 1):img_data_byte_num * i]
            packet = message_size + message_id + seq_no + m_inum + offset + bits

            self.socket.sendto(packet, (self.DMD_IP, self.UDP_PORT_DATA))

            if delay:
                time.sleep(delay)

    def load_image(self, inum, image, delay=None):
        """

        Parameters
        ----------
        inum : int
        image : str, numpy.ndarray
        delay : float
        """
        if isinstance(image, str):
            image = open(image, 'rb').read()
        elif isinstance(image, np.ndarray):
            if image.dtype == np.bool:
                image = np.packbits(image).tobytes()
        else:
            raise TypeError("Image must be a string path to a .bin file or a numpy ndarray with bool dtype.")

        if self.inverse:
            image_inv = []
            for bt in image:
                image_inv.append(~bt + 256)
            image = bytes(image_inv)

        self.send_packet(112)
        self.recv_ack()

        # Determine how many lines of the image data can be packed into each packet
        # 14 bytes for th header, so 8986 = 9000 - 14 and 1486 = 1500 - 14
        img_data_line_num = 8986//(self._cols//8) if self.jumbo_frame else 1486//(self._cols//8)

        # Calculate how many image packets need to be sent.
        packet_num = self._rows // img_data_line_num
        assert self._rows % img_data_line_num == 0 # TODO: implement the case that last packet has less data

        self._send_image_packets(1, packet_num, inum, image, img_data_line_num, delay=delay)

        while True:
            self.send_packet(311)
            rec_id, payload = self.recv_packet()
            assert rec_id == 511
            if payload[0] == 0:
                break
            else:
                last_seq_no = payload[1:3]
                self._send_image_packets(last_seq_no + 1, packet_num, inum, image, img_data_line_num, delay=delay)

    def set_sequencer_state(self, seq_cmd, enable):
        """This function is used to manipulate the status of the sequencer in Luxbeam.

        Parameters
        ----------
        seq_cmd : int
            Command to send. See table below for valid commands.
                1: When enabled, the sequencer will start running from its current position.
                When disabled, the sequencer will stop at its current position.
                2: When enabled, the sequencer will enter its <<reset>>-state.
                When disabled, the sequencer will be taken out of its <<reset>>-state.
        enable : int
            ENABLE or DISABLE

        Raises
        ------
        :obj:`Luxbeam.luxbeam.LuxbeamError`
            If an invalid seq_cmd is sent in <<SetSequencerState>>, a <<ReplyAck>> with error number 10006
            (Invalid sequence command) will be returned.
        """
        payload = seq_cmd.to_bytes(1, byteorder='big') + enable.to_bytes(1, byteorder='big')
        self.send_packet(106, payload)
        self.recv_ack()

    def set_safe_shutdown(self):
        """This function will make the Luxbeam go into a mode where it is safe to remove the power-supply.

        This mode should always be entered before powering-off the product. Note that after entering this mode, the product
        will no longer respond to any communication and must be power off and on to function normally again. The
        LEDs will alternately flash red and yellow when in shutdown-mode.
        Returns
        -------
        """
        self.send_packet(180)
        self.recv_ack()

    def get_network_settings(self):
        """

        Returns
        -------
        ip_addr: str
        subnet: str
        gateway: str
        dhcp: int
            ENABLE: DHCP is enabled.
            DISABLE: DHCP is DISABLED.

        """
        self.send_packet(308)
        rec_id, payload = self.recv_packet()
        assert rec_id == 508
        ip_addr = ipaddress.IPv4Address(payload[3::-1])
        subnet = ipaddress.IPv4Address(payload[7:3:-1])
        gateway = ipaddress.IPv4Address(payload[11:7:-1])
        dhcp = int(payload[12])
        return str(ip_addr), str(subnet), str(gateway), dhcp

    def set_network_settings(self, ip_addr=None, subnet=None, gateway=None, dhcp=0):
        """

        Parameters
        ----------
        ip_addr
        subnet
        gateway
        dhcp
        Returns
        -------
        """
        if dhcp == ENABLE:
            ip_addr, subnet, gateway = ["0.0.0.0"] * 3
        ip_addr = ipaddress.IPv4Address(ip_addr).packed[::-1]
        subnet = ipaddress.IPv4Address(subnet).packed[::-1]
        gateway = ipaddress.IPv4Address(gateway).packed[::-1]
        dhcp = dhcp.to_bytes(1, byteorder='big')
        payload = ip_addr + subnet + gateway + dhcp
        self.send_packet(108, payload)
        self.recv_ack()

    def save_settings(self):
        """This record is used to store parameters that are marked <<Permanent>> in nonvolatile memory."""
        self.send_packet(110)
        self.recv_ack()

    def set_factory_defaluts(self):
        """This function will reset parameters back to factory defaults and store these values in nonvolatile memory
        This will reset the parameters that are marked as <<permanent>> back to its default settings.
        """
        self.send_packet(113)
        self.recv_ack()

    def get_dmd_mirror_shake(self):
        self.send_packet(395)
        rec_id, payload = self.recv_packet()
        assert rec_id == 595
        enable = int(payload[0])
        return enable

    def set_dmd_mirror_shake(self, enable):
        payload = enable.to_bytes(1, byteorder='big')
        self.send_packet(195, payload)
        self.recv_ack()

    def set_software_sync(self, level):
        payload = level.to_bytes(1, byteorder='big')
        self.send_packet(120, payload)
        self.recv_ack()

    def get_software_sync(self):
        self.send_packet(320)
        rec_id, payload = self.recv_packet()
        assert rec_id == 520
        level = int(payload)
        return level
