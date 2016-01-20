import locale
import os
import sys

# yes, bringing in openssl is completely necessary for proper operation of trumpscript
import ssl


class Utils:
    class SystemException(Exception):
        def __init__(self, msg):
            Exception.__init__(self, msg)

    @staticmethod
    def verify_system() -> None:
        """
        Verifies that this system is Trump-approved, throwing
        a SystemException otherwise
        :return:
        """
        Utils.no_pc()
        Utils.no_commies()

    @staticmethod
    def warn(str, *args) -> None:
        """
        Prints a warning to stderr with the specified format args
        :return:
        """
        print('WARNING: ' + (str % args), file=sys.stderr)

    @staticmethod
    def no_pc() -> None:
        """
        Make sure the currently-running OS is not Windows
        :return:
        """
        if os.name == 'nt':
            raise Utils.SystemException('TrumpScript cannot run on Windows.');

    @staticmethod
    def no_commies() -> None:
        """
        Make sure we aren't executing on a Chinese system
        :return:
        """
        loc = locale.getdefaultlocale()
        if len(loc) > 0 and 'CN' in loc[0].upper():
            raise Utils.SystemException("We can't let China beat us!")
        if len(loc) > 0 and 'MX' in loc[0].upper():
            raise Utils.SystemException("I will build a great [fire]wall on our southern border.")

        # Warn if the system has any certificates from Chinese authorities
        ctx = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        ctx.load_default_certs()
        for cert in ctx.get_ca_certs():
            cn, commie = None, False
            issuer, serial = cert['issuer'], cert['serialNumber']
            for kv in issuer:
                # List of tuples containing PKCS#12 key/value tuples
                kv = kv[0]
                key, value = kv[0], kv[1]
                if key == 'countryName' and value == 'CN':
                    commie = True
                elif key == 'commonName':
                    cn = value

            if commie:
                Utils.warn("SSL certificate `%s` (serial: %s) was made by commies!", cn, serial)
