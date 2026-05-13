import unittest
import unittest.mock
from password_checker import PasswordPolicy, PasswordChecker, get_valid_int, get_yes_no, main


class TestPasswordPolicy(unittest.TestCase):

    # TEST 1: Default policy has correct values
    def test_default_policy_values(self):
        policy = PasswordPolicy()
        self.assertEqual(policy.min_length, 8)
        self.assertEqual(policy.max_length, 128)
        self.assertTrue(policy.require_uppercase)
        self.assertTrue(policy.require_lowercase)
        self.assertTrue(policy.require_digit)
        self.assertTrue(policy.require_special)

    # TEST 2: Custom policy stores values correctly
    def test_custom_policy_values(self):
        policy = PasswordPolicy(min_length=12, require_special=False)
        self.assertEqual(policy.min_length, 12)
        self.assertFalse(policy.require_special)

    # TEST 3: describe() doesn't crash
    def test_describe_does_not_crash(self):
        policy = PasswordPolicy()
        try:
            policy.describe()
        except Exception as e:
            self.fail(f"describe() raised an exception: {e}")


class TestPasswordChecker(unittest.TestCase):

    def setUp(self):
        """Create a default policy and checker before each test."""
        self.policy  = PasswordPolicy()
        self.checker = PasswordChecker(self.policy)

    # TEST 4: Strong password passes all checks
    def test_strong_password_passes(self):
        result = self.checker.check("Secure@123")
        self.assertTrue(result["passed"])
        self.assertEqual(len(result["failures"]), 0)

    # TEST 5: Short password fails min length check
    def test_short_password_fails(self):
        result = self.checker.check("Ab1!")
        self.assertFalse(result["passed"])
        self.assertTrue(any("short" in f.lower() for f in result["failures"]))

    # TEST 6: Password without uppercase fails
    def test_missing_uppercase_fails(self):
        result = self.checker.check("secure@123")
        self.assertFalse(result["passed"])
        self.assertTrue(any("uppercase" in f.lower() for f in result["failures"]))

    # TEST 7: Password without lowercase fails
    def test_missing_lowercase_fails(self):
        result = self.checker.check("SECURE@123")
        self.assertFalse(result["passed"])
        self.assertTrue(any("lowercase" in f.lower() for f in result["failures"]))

    # TEST 8: Password without digit fails
    def test_missing_digit_fails(self):
        result = self.checker.check("Secure@abc")
        self.assertFalse(result["passed"])
        self.assertTrue(any("number" in f.lower() for f in result["failures"]))

    # TEST 9: Password without special char fails
    def test_missing_special_char_fails(self):
        result = self.checker.check("Secure1234")
        self.assertFalse(result["passed"])
        self.assertTrue(any("special" in f.lower() for f in result["failures"]))

    # TEST 10: Password exceeding max length fails
    def test_too_long_password_fails(self):
        policy  = PasswordPolicy(max_length=10)
        checker = PasswordChecker(policy)
        result  = checker.check("A" * 11 + "a1!")
        self.assertFalse(result["passed"])
        self.assertTrue(any("long" in f.lower() for f in result["failures"]))

    # TEST 11: Weak password gets weak strength rating
    def test_weak_password_strength(self):
        result = self.checker.check("abc")
        self.assertIn("Weak", result["strength"])

    # TEST 12: Strong password gets strong strength rating
    def test_strong_password_strength(self):
        result = self.checker.check("Secure@123")
        self.assertIn("Strong", result["strength"])

    # TEST 13: display_result doesn't crash
    def test_display_result_does_not_crash(self):
        try:
            self.checker.display_result("Secure@123")
        except Exception as e:
            self.fail(f"display_result raised an exception: {e}")

    # TEST 14: Policy with no requirements accepts any password
    def test_permissive_policy_accepts_anything(self):
        policy  = PasswordPolicy(
            min_length=1,
            require_uppercase=False,
            require_lowercase=False,
            require_digit=False,
            require_special=False
        )
        checker = PasswordChecker(policy)
        result  = checker.check("abc")
        self.assertTrue(result["passed"])


class TestInputValidation(unittest.TestCase):

    # TEST 15: get_valid_int returns correct value
    def test_get_valid_int(self):
        with unittest.mock.patch("builtins.input", return_value="10"):
            result = get_valid_int("Enter: ", 1, 100)
            self.assertEqual(result, 10)

    # TEST 16: get_yes_no returns True for "y"
    def test_get_yes_no_yes(self):
        with unittest.mock.patch("builtins.input", return_value="y"):
            result = get_yes_no("Yes or no? ")
            self.assertTrue(result)

    # TEST 17: get_yes_no returns False for "n"
    def test_get_yes_no_no(self):
        with unittest.mock.patch("builtins.input", return_value="n"):
            result = get_yes_no("Yes or no? ")
            self.assertFalse(result)


class TestMainMenu(unittest.TestCase):

    # TEST 18: Main menu option 1 - check password
    def test_main_check_password(self):
        inputs = iter(["1", "Secure@123", "4"])
        with unittest.mock.patch("builtins.input", lambda _: next(inputs)):
            try:
                main()
            except Exception as e:
                self.fail(f"main() raised an exception: {e}")

    # TEST 19: Main menu option 2 - view policy
    def test_main_view_policy(self):
        inputs = iter(["2", "4"])
        with unittest.mock.patch("builtins.input", lambda _: next(inputs)):
            try:
                main()
            except Exception as e:
                self.fail(f"main() raised an exception: {e}")

    # TEST 20: Main menu invalid option then quit
    def test_main_invalid_option(self):
        inputs = iter(["9", "4"])
        with unittest.mock.patch("builtins.input", lambda _: next(inputs)):
            try:
                main()
            except Exception as e:
                self.fail(f"main() raised an exception: {e}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
