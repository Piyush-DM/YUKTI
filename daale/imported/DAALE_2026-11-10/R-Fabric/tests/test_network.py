"""IPv4-only connections, for networks where IPv6 does not work. No network: sockets are stubbed."""

import io
import socket
import unittest
from unittest import mock

import urllib3.util.connection as urllib3_connection

import live_check
from daale import network
from daale.providers import build_live_client

LOCAL = {"DAALE_LIVE_PROVIDER": "generic", "LLM_BASE_URL": "http://127.0.0.1:1/v1"}
V6 = (socket.AF_INET6, socket.SOCK_STREAM, 6, "", ("2001:db8::1", 443, 0, 0))
V4 = (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("192.0.2.1", 443))


class RestoresTheResolver(unittest.TestCase):
    """``force_ipv4`` replaces a urllib3 function for the whole process, so each test puts it back."""

    def setUp(self):
        self.original = urllib3_connection.allowed_gai_family
        self.addCleanup(setattr, urllib3_connection, "allowed_gai_family", self.original)


class ForceIpv4Tests(RestoresTheResolver):
    def test_urllib3_then_asks_for_ipv4_addresses_only(self):
        network.force_ipv4()
        with mock.patch("socket.getaddrinfo", return_value=[]) as lookup:
            with self.assertRaises(OSError):
                urllib3_connection.create_connection(("daale.invalid", 443), 1)
        self.assertEqual(lookup.call_args.args[2], socket.AF_INET)

    def test_nothing_changes_unless_the_environment_asks(self):
        build_live_client(dict(LOCAL))
        self.assertIs(urllib3_connection.allowed_gai_family, self.original)

    def test_the_environment_switch_turns_it_on(self):
        build_live_client({**LOCAL, "DAALE_FORCE_IPV4": "true"})
        self.assertEqual(urllib3_connection.allowed_gai_family(), socket.AF_INET)

    def test_a_false_switch_leaves_it_alone(self):
        build_live_client({**LOCAL, "DAALE_FORCE_IPV4": "false"})
        self.assertIs(urllib3_connection.allowed_gai_family, self.original)


class Ipv6DiagnosisTests(unittest.TestCase):
    def diagnose(self, addresses, refuses=("2001:db8::1",), unresolvable=False):
        """Run ipv6_is_broken against stub sockets: connections to ``refuses`` time out, others succeed."""

        def connect(address, timeout):
            if address[0] in refuses:
                raise TimeoutError("timed out")
            return mock.MagicMock()

        lookup = mock.patch("socket.getaddrinfo", side_effect=OSError("no such host") if unresolvable else None,
                            return_value=addresses)
        with lookup, mock.patch("socket.create_connection", side_effect=connect) as attempts:
            return network.ipv6_is_broken("https://example.test/v1"), attempts

    def test_dead_ipv6_with_working_ipv4_is_reported(self):
        broken, _ = self.diagnose([V6, V4])
        self.assertTrue(broken)

    def test_working_ipv6_is_not_reported(self):
        broken, _ = self.diagnose([V6, V4], refuses=())
        self.assertFalse(broken)

    def test_a_host_without_ipv6_is_not_reported_and_nothing_is_tried(self):
        broken, attempts = self.diagnose([V4])
        self.assertFalse(broken)
        attempts.assert_not_called()

    def test_both_families_failing_is_not_blamed_on_ipv6(self):
        broken, _ = self.diagnose([V6, V4], refuses=("2001:db8::1", "192.0.2.1"))
        self.assertFalse(broken)

    def test_a_name_that_does_not_resolve_is_not_reported(self):
        broken, _ = self.diagnose([], unresolvable=True)
        self.assertFalse(broken)

    def test_no_url_means_no_verdict(self):
        self.assertFalse(network.ipv6_is_broken(None))


class LiveCheckSwitchTests(RestoresTheResolver):
    def run_switch(self, env, broken):
        out = io.StringIO()
        with mock.patch("live_check.ipv6_is_broken", return_value=broken) as probe:
            switched = live_check.use_ipv4_if_needed(env, out)
        return switched, out.getvalue(), probe

    def test_a_dead_ipv6_route_switches_the_run_to_ipv4_and_says_how_to_keep_it(self):
        switched, message, _ = self.run_switch({"LLM_BASE_URL": "https://example.test/v1"}, broken=True)
        self.assertTrue(switched)
        self.assertEqual(urllib3_connection.allowed_gai_family(), socket.AF_INET)
        self.assertIn("DAALE_FORCE_IPV4=true", message)

    def test_a_working_network_is_left_alone(self):
        switched, message, _ = self.run_switch({"LLM_BASE_URL": "https://example.test/v1"}, broken=False)
        self.assertFalse(switched)
        self.assertEqual(message, "")
        self.assertIs(urllib3_connection.allowed_gai_family, self.original)

    def test_nothing_is_probed_when_the_environment_already_forces_ipv4(self):
        switched, _, probe = self.run_switch(
            {"LLM_BASE_URL": "https://example.test/v1", "DAALE_FORCE_IPV4": "true"}, broken=True
        )
        self.assertFalse(switched)
        probe.assert_not_called()


if __name__ == "__main__":
    unittest.main()
