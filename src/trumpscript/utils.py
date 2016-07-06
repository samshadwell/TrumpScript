import locale
import os
import platform
import random
import sys

# yes, bringing in openssl is completely necessary for proper operation of trumpscript
import ssl

from trumpscript.constants import ERROR_CODES

class Utils:
    class SystemException(Exception):
        def __init__(self, msg_code) -> Exception:
            """
            Get the error from the error code and throw Exception
            :param msg_code: the code for the error
            :return: The new Exception
            """
            if msg_code in ERROR_CODES:
                Exception(random.choice(ERROR_CODES[msg_code]))
            else:
                Exception(random.choice(ERROR_CODES['default']))

    @staticmethod
    def verify_system(wall) -> None:
        """
        Verifies that this system is Trump-approved, throwing
        a SystemException otherwise
        :return:
        """
        Utils.no_wimps()
        Utils.no_pc()
        Utils.boycott_apple()
        Utils.no_commies_mexicans_or_kenyans(wall)
        Utils.no_commie_network()

    @staticmethod
    def warn(str, *args) -> None:
        """
        Prints a warning to stderr with the specified format args
        :return:
        """
        print('WARNING: ' + (str % args), file=sys.stderr)

    @staticmethod
    def no_wimps() -> None:
        """
        Make sure we're not executing as root, because America is strong
        :return:
        """
        if os.name != 'nt' and os.geteuid() == 0:
            raise Utils.SystemException('root')

    @staticmethod
    def no_pc() -> None:
        """
        Make sure the currently-running OS is not Windows, because we're not PC
        :return:
        """
        if os.name == 'nt':
            raise Utils.SystemException('os');

    @staticmethod
    def boycott_apple() -> None:
        """
        Boycott all Apple products  until such time as Apple gives cellphone
        info to authorities regarding radical Islamic terrorist couple from Cal
        :return:
        """
        if platform.system() == "Darwin":
            raise Utils.SystemException('boycott');

    @staticmethod
    def no_commies_mexicans_or_kenyans(wall) -> None:
        """
        Make sure we aren't executing on a Chinese or Mexican system, because
        America has traditional values.
        If we have a Kenyan SSL root on our system, refuse to run entirely,
        because we can't have that, can we?
        :return:
        """
        loc = locale.getdefaultlocale()
        loc = loc[0].upper() if len(loc) > 0 else ''
        if 'CN' in loc:
            raise Utils.SystemException("We can't let China beat us!")
        elif 'MX' in loc and wall:
            raise Utils.SystemException("I will build a great [fire]wall on our southern border.")

        # Warn if the system has any certificates from Chinese authorities.
        # If the system has any certificates from Kenyan authorities,
        # refuse to run entirely.
        ctx = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        ctx.load_default_certs()
        for cert in ctx.get_ca_certs():
            cn, commie = None, False
            issuer, serial = cert['issuer'], cert['serialNumber']
            for kv in issuer:
                # List of tuples containing PKCS#12 key/value tuples
                kv = kv[0]
                key, value = kv[0], kv[1]
                if key == 'countryName':
                    if value == 'CN':
                        commie = True
                    elif value == 'KE':
                        raise Utils.SystemException('ssl')
                elif key == 'commonName':
                    cn = value

            if commie:
                Utils.warn("SSL certificate `%s` (serial: %s) was made by commies!", cn, serial)

    @staticmethod
    def no_commie_network() -> None:
        """
        Make sure we aren't running on commie Chinese networks.
        """
        freedom_host = "facebook.com"
        commie_host = "alibaba.cn"
        is_on_a_network = os.system("ping -c 1 {}".format(commie_host)) == 0
        is_commie_network = os.system("ping -c 1 {}".format(freedom_host)) != 0
        if is_on_a_network and is_commie_network:
            raise Utils.SystemException("Detected commie network, aborting.")

