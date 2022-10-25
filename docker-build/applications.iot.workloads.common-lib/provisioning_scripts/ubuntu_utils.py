"""
Copyright: 2019-2022 Intel Corporation
Author: Amit Kumar <amit2.kumar@intel.com> [16 Feb 2022]

utility for ubuntu
"""
import platform
import argparse
import os

from star_fw.framework_base.logger.api_intf_logger import LoggerAPI
from star_fw.framework_base.test_interface.api_intf_test_interface import TestInterfaceAPI
from star_fw.framework_base.star_decorator import StarDecorator


class UbuntuUtils:
    """
    utility class for Ubuntu

    """
    def __init__(self,device_tag="utils", os_name: str = None, test_interface_obj: any = None) -> None:
        """
        UbuntuUtils class initialization
        
        :param str device_tag: device tag, defaults to "utils"
        :param str os_name: platform os, defaults to None
        :param any test_interface_obj: test interface object , defaults to None
        
        """
        self.log = LoggerAPI()
        self.log.debug(f'Logger File Path: {self.log.get_log_folder_path()}')
        self.tif = test_interface_obj
        self.os_name = os_name
        self.username = os.getlogin()
        if self.os_name is None:
            self.os_name = platform.system().lower()
        if self.tif is None:
            self.tif = TestInterfaceAPI(intf_type='local', os_name=self.os_name, device_tag=device_tag)

    def increase_ssh_count(self, max: str = '100') -> None:
        """
        This method will set the MaxSessions variable in /etc/ssh/sshd_config file.
        
        :param int max: Number of session, defaults to 100
        
        """
        StarDecorator.single_blocked_print('updating sshd_config File')
        file_path = "/etc/ssh/sshd_config"
        cmd = f"sudo sed -i -r 's/(#)?MaxSessions [0-9]+/MaxSessions {max}/g' {file_path}"
        try:
            output_dict = self.tif.execute(cmd, timeout=60)
            if output_dict["status"] is False:
                self.log.error(f'failed to execute command {cmd}')
                raise Exception(f'failed to execute command {cmd}')
            else:
                self.log.info('updated /etc/ssh/sshd_config')

            cmd = f"sudo systemctl restart ssh"
            self.tif.execute(cmd, timeout=60)
        except Exception as e:
            self.log.error(f'failed to increase ssh count! [ {e} ]')
            raise Exception(f'failed to increase ssh count! [ {e} ]')

    def disable_lock_screen(self) -> dict:
        """
        Method to disable the lock screen

        :usage:
            disk_utils_obj.disable_lock_screen()

        :return: dict with below key-value  pairs
            "status" (bool): True if lock screen is disabled successfully else False.
            "msg" (str): Failure msg

        """
        sts_dict = {
            'status': False,
            'msg': ''
        }
        get_uid_cmd = self.tif.execute(command=f'id -u {self.username}',timeout=15)
        uid = get_uid_cmd.get('output').strip()

        lock_disable_sts = self.tif.execute(command=f'sudo -u {self.username} DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/{uid}/bus" gsettings set org.gnome.desktop.screensaver lock-enabled false',
                                            timeout=15)
        if not lock_disable_sts.get('status', False):
            sts_dict['msg'] = f'Failed to execute disable lock Screen command....'
            return sts_dict

        check_sts = self.tif.execute(command='gsettings get org.gnome.desktop.screensaver lock-enabled', timeout=15)
        if not check_sts.get('status', False):
            sts_dict['msg'] = f'Failed to get the status of lock Screen....'
            return sts_dict

        if check_sts.get('output').strip().lower() != 'false':
            sts_dict['msg'] = f'lock screen is not set properly: {check_sts.get("output")}'
            return sts_dict

        sts_dict['status'] = True
        return sts_dict

    
    def disable_screen_inactivity_timeout(self) -> dict:
        """
        Method to disable the feature which turns off the screen after period of inactivity.

        # :usage:
        #     disk_utils_obj.disable_screen_inactivity_timeout()

        :return: dict with below key-value  pairs
            "status" (bool): True if screen activity timeout is disabled successfully else False.
            "msg" (str): Failure msg

        """
        sts_dict = {
            'status': False,
            'msg': ''
        }
        get_uid_cmd = self.tif.execute(command=f'id -u {self.username}',timeout=15)
        uid = get_uid_cmd.get('output').strip()
                                
        timeout_disable_sts = self.tif.execute(command=f'sudo -u {self.username} DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/{uid}/bus" gsettings set org.gnome.desktop.session idle-delay 0',
                                            timeout=15)
        if not timeout_disable_sts.get('status', False):
            sts_dict['msg'] = f'Failed to execute ....'
            return sts_dict

        check_sts = self.tif.execute(command=f'sudo -u {self.username} DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/{uid}/bus" gsettings get org.gnome.desktop.session idle-delay', timeout=15)
        if not check_sts.get('status', False):
            sts_dict['msg'] = f'Failed to get the status ....'
            return sts_dict

        if check_sts.get('output').strip().lower() != 'uint32 0':
            sts_dict['msg'] = f'lock screen is not set properly: {check_sts.get("output")}'
            return sts_dict

        sts_dict['status'] = True
        return sts_dict

    def disable_automatic_suspend(self) -> dict:
        """
        Method to disable the feature which pauses the computer after period of inactivity.

        # :usage:
        #     disk_utils_obj.disable_lock_screen()

        :return: dict with below key-value  pairs
            "status" (bool): True if lock screen is disabled successfully else False.
            "msg" (str): Failure msg listing failed unmount of partitions

        """
        sts_dict = {
            'status': False,
            'msg': ''
        }
        get_uid_cmd = self.tif.execute(command=f'id -u {self.username}',timeout=15)
        uid = get_uid_cmd.get('output').strip()
        auto_suspend_disable_ac_type_sts = self.tif.execute(command=f'sudo -u {self.username} DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/{uid}/bus" gsettings set org.gnome.settings-daemon.plugins.power sleep-inactive-ac-type \'nothing\'',
                                            timeout=15)
        auto_suspend_disable_battery_type_sts = self.tif.execute(command=f'sudo -u {self.username} DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/{uid}/bus" gsettings set org.gnome.settings-daemon.plugins.power sleep-inactive-battery-type \'nothing\'',
                                            timeout=15)
        if not (auto_suspend_disable_ac_type_sts.get('status', False) and auto_suspend_disable_battery_type_sts.get('status', False)):
            sts_dict['msg'] = f'Failed to execute ....'
            return sts_dict

        check_ac_sts = self.tif.execute(command=f'sudo -u {self.username} DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/{uid}/bus" gsettings get org.gnome.settings-daemon.plugins.power sleep-inactive-ac-type', timeout=15)
        check_battery_sts = self.tif.execute(command=f'sudo -u {self.username} DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/{uid}/bus" gsettings get org.gnome.settings-daemon.plugins.power sleep-inactive-battery-type', timeout=15)
        if not (check_ac_sts.get('status', False) and check_battery_sts.get('status', False)):
            sts_dict['msg'] = f'Failed to get the status ....'
            return sts_dict

        if (check_ac_sts.get('output').strip().lower() != '\'nothing\'') and (check_battery_sts.get('output').strip().lower() != '\'nothing\''):
            sts_dict['msg'] = f'property is not set properly: AC: {check_ac_sts.get("output")} | Battery : {check_battery_sts.get("output")}'
            return sts_dict

        sts_dict['status'] = True
        return sts_dict

    def disable_screen_dimming(self) -> dict:
        """
        Method to disable the feature which reduces the screen brightness the computer is inactive.

        # :usage:
        #     disk_utils_obj.disable_lock_screen()

        :return: dict with below key-value  pairs
            "status" (bool): True if lock screen is disabled successfully else False.
            "msg" (str): Failure msg listing failed unmount of partitions

        """
        sts_dict = {
            'status': False,
            'msg': ''
        }
        get_uid_cmd = self.tif.execute(command=f'id -u {self.username}',timeout=15)
        uid = get_uid_cmd.get('output').strip()
        screen_dimming_disable_sts = self.tif.execute(command=f'sudo -u {self.username} DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/{uid}/bus" gsettings set org.gnome.settings-daemon.plugins.power idle-dim false',
                                            timeout=15)
        if not screen_dimming_disable_sts.get('status', False):
            sts_dict['msg'] = f'Failed to execute disable lock Screen command....'
            return sts_dict

        check_sts = self.tif.execute(command=f'sudo -u {self.username} DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/{uid}/bus" gsettings get org.gnome.settings-daemon.plugins.power idle-dim', timeout=15)
        if not check_sts.get('status', False):
            sts_dict['msg'] = f'Failed to get the status of lock Screen....'
            return sts_dict

        if check_sts.get('output').strip().lower() != 'false':
            sts_dict['msg'] = f'lock screen is not set properly: {check_sts.get("output")}'
            return sts_dict

        sts_dict['status'] = True
        return sts_dict

    def disable_power_saver(self) -> dict:
        """
        Method to disable the feature which switches on power saver on low battery.

        # :usage:
        #     disk_utils_obj.disable_power_saver()

        :return: dict with below key-value  pairs
            "status" (bool): True if disabled successfully else False.
            "msg" (str): Failure msg

        """
        sts_dict = {
            'status': False,
            'msg': ''
        }
        get_uid_cmd = self.tif.execute(command=f'id -u {self.username}',timeout=15)
        uid = get_uid_cmd.get('output').strip()
        power_saver_disable_sts = self.tif.execute(command=f'sudo -u {self.username} DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/{uid}/bus" gsettings set org.gnome.settings-daemon.plugins.power power-saver-profile-on-low-battery false',
                                            timeout=15)
        if not power_saver_disable_sts.get('status', False):
            sts_dict['msg'] = f'Failed to execute command....'
            return sts_dict

        check_sts = self.tif.execute(command=f'sudo -u {self.username} DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/{uid}/bus" gsettings get org.gnome.settings-daemon.plugins.power power-saver-profile-on-low-battery', timeout=15)
        if not check_sts.get('status', False):
            sts_dict['msg'] = f'Failed to get the status ....'
            return sts_dict

        if check_sts.get('output').strip().lower() != 'false':
            sts_dict['msg'] = f'property is not set properly: {check_sts.get("output")}'
            return sts_dict

        sts_dict['status'] = True
        return sts_dict

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--count', help='SSH COUNT', default=100, type=int)
    parser.add_argument('-dl', help='disable lock screen', default=True, type=bool)
    parser.add_argument('-ds', help='disable screen inactivity timeout', default=True, type=bool)
    parser.add_argument('-da', help='disable auto suspend', default=True, type=bool)
    parser.add_argument('-dd', help='disable screen dimming', default=True, type=bool)
    parser.add_argument('-dp', help='disable power saver', default=True, type=bool)
    args, _ = parser.parse_known_args()

    obj = UbuntuUtils()
    obj.increase_ssh_count(max=args.count)

    if args.dl:
        obj.disable_lock_screen()
    if args.ds:
        obj.disable_screen_inactivity_timeout()
    if args.da:
        obj.disable_automatic_suspend()
    if args.dd:
        obj.disable_screen_dimming()
    if args.dp:
        obj.disable_power_saver()
