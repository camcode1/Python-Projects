import re  # Built-in library for pattern matching (checking characters in passwords)

# ─────────────────────────────────────────────
# CLASS 1: PasswordPolicy
# Stores the rules a password must follow
# Think of this as a "settings" object
# ─────────────────────────────────────────────

class PasswordPolicy:
    def __init__(
        self,
        min_length=8,           # Password must be at least this many characters
        require_uppercase=True, # Must contain at least one uppercase letter (A-Z)
        require_lowercase=True, # Must contain at least one lowercase letter (a-z)
        require_digit=True,     # Must contain at least one number (0-9)
        require_special=True,   # Must contain at least one special character (!@#$ etc.)
        max_length=128          # Password cannot exceed this length
    ):
        self.min_length       = min_length
        self.require_uppercase = require_uppercase
        self.require_lowercase = require_lowercase
        self.require_digit    = require_digit
        self.require_special  = require_special
        self.max_length       = max_length

    def describe(self):
        """Print a summary of the current policy rules."""
        print("\n📋 Current Password Policy:")
        print(f"  Min length:        {self.min_length}")
        print(f"  Max length:        {self.max_length}")
        print(f"  Require uppercase: {self.require_uppercase}")
        print(f"  Require lowercase: {self.require_lowercase}")
        print(f"  Require digit:     {self.require_digit}")
        print(f"  Require special:   {self.require_special}")


# ─────────────────────────────────────────────
# CLASS 2: PasswordChecker
# Takes a policy and checks passwords against it
# Think of this as the "engine" that does the work
# ─────────────────────────────────────────────

class PasswordChecker:
    # Special characters that satisfy the special character requirement
    SPECIAL_CHARS = r"[!@#$%^&*(),.?\":{}|<>]"

    def __init__(self, policy: PasswordPolicy):
        self.policy = policy    # Store the policy so we can reference its rules

    def check(self, password: str) -> dict:
        """
        Evaluate a password against the policy.
        Returns a dictionary with:
          - 'passed': True/False overall result
          - 'failures': list of rules the password broke
          - 'strength': "Weak", "Moderate", or "Strong"
          - 'score': numeric score out of 5
        """
        failures = []   # Collect all the rules this password breaks
        score    = 0    # Track how many checks it passes (used for strength rating)

        # ── Check 1: Minimum length ──
        if len(password) < self.policy.min_length:
            failures.append(f"Too short (min {self.policy.min_length} characters)")
        else:
            score += 1  # Passed this check

        # ── Check 2: Maximum length ──
        if len(password) > self.policy.max_length:
            failures.append(f"Too long (max {self.policy.max_length} characters)")

        # ── Check 3: Uppercase letter ──
        if self.policy.require_uppercase and not re.search(r"[A-Z]", password):
            failures.append("Missing uppercase letter (A-Z)")
        elif self.policy.require_uppercase:
            score += 1  # Has at least one uppercase

        # ── Check 4: Lowercase letter ──
        if self.policy.require_lowercase and not re.search(r"[a-z]", password):
            failures.append("Missing lowercase letter (a-z)")
        elif self.policy.require_lowercase:
            score += 1  # Has at least one lowercase

        # ── Check 5: Digit ──
        if self.policy.require_digit and not re.search(r"[0-9]", password):
            failures.append("Missing a number (0-9)")
        elif self.policy.require_digit:
            score += 1  # Has at least one digit

        # ── Check 6: Special character ──
        if self.policy.require_special and not re.search(self.SPECIAL_CHARS, password):
            failures.append("Missing special character (!@#$%^&* etc.)")
        elif self.policy.require_special:
            score += 1  # Has at least one special character

        # ── Determine strength based on score ──
        if score <= 2:
            strength = "Weak 🔴"
        elif score <= 3:
            strength = "Moderate 🟡"
        else:
            strength = "Strong 🟢"

        return {
            "passed":   len(failures) == 0,  # True only if zero failures
            "failures": failures,
            "strength": strength,
            "score":    score
        }

    def display_result(self, password: str):
        """Run check() and print the results in a readable format."""
        result = self.check(password)

        print(f"\n🔐 Password: {'*' * len(password)}")   # Mask password for security
        print(f"   Strength: {result['strength']} ({result['score']}/5)")

        if result["passed"]:
            print("   ✅ Password meets all policy requirements!")
        else:
            print("   ❌ Password failed the following checks:")
            for failure in result["failures"]:
                print(f"      • {failure}")             # List each failed rule


# ─────────────────────────────────────────────
# INPUT VALIDATION
# Make sure user input is safe before using it
# ─────────────────────────────────────────────

def get_valid_int(prompt, min_val=1, max_val=999):
    """Keep asking until the user enters a valid integer in range."""
    while True:
        try:
            value = int(input(prompt))              # Try to convert input to int
            if min_val <= value <= max_val:
                return value
            else:
                print(f"  Please enter a number between {min_val} and {max_val}.")
        except ValueError:
            print("  Invalid input — please enter a number.")  # Catch non-numeric input

def get_yes_no(prompt):
    """Ask a yes/no question and return True for yes, False for no."""
    while True:
        answer = input(prompt).strip().lower()  # Normalize to lowercase
        if answer in ("y", "yes"):
            return True
        elif answer in ("n", "no"):
            return False
        else:
            print("  Please enter y or n.")


# ─────────────────────────────────────────────
# CLI MENU
# ─────────────────────────────────────────────

def main():
    # Start with a default policy — user can customize it from the menu
    policy  = PasswordPolicy()
    checker = PasswordChecker(policy)   # Create checker using the default policy

    print("🔒 Welcome to the Password Strength & Policy Checker")

    while True:
        print("\n====== Main Menu ======")
        print("1. Check a password")
        print("2. View current policy")
        print("3. Customize policy")
        print("4. Quit")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            # ── Check a password ──
            password = input("Enter password to check: ")   # Input validation handled in check()
            checker.display_result(password)

        elif choice == "2":
            # ── Show the current policy rules ──
            policy.describe()

        elif choice == "3":
            # ── Let user customize the policy ──
            print("\n⚙️  Customize Policy (press Enter to keep current value)")
            policy.min_length       = get_valid_int(f"Min length [{policy.min_length}]: ", 1, 100)
            policy.max_length       = get_valid_int(f"Max length [{policy.max_length}]: ", 8, 999)
            policy.require_uppercase = get_yes_no("Require uppercase? (y/n): ")
            policy.require_lowercase = get_yes_no("Require lowercase? (y/n): ")
            policy.require_digit    = get_yes_no("Require digit? (y/n): ")
            policy.require_special  = get_yes_no("Require special char? (y/n): ")
            checker = PasswordChecker(policy)   # Rebuild checker with updated policy
            print("✅ Policy updated!")

        elif choice == "4":
            print("Goodbye! 👋")
            break

        else:
            print("Invalid option, please try again.")


if __name__ == "__main__":
    main()
