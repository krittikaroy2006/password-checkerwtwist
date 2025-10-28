import string
import random
import time
import streamlit as st

LEAK_FILE = "leaked_passwords.txt"
COOLDOWN_SECONDS = 3600  # 1 hour lockout (for display only)

def check_password_strength(password):
    length_error = len(password) < 8
    uppercase_error = not any(ch.isupper() for ch in password)
    lowercase_error = not any(ch.islower() for ch in password)
    digit_error = not any(ch.isdigit() for ch in password)
    special_error = not any(ch in string.punctuation for ch in password)

    feedback = []
    if length_error:
        feedback.append("Password should be at least 8 characters long.")
    if uppercase_error:
        feedback.append("Add at least one uppercase letter.")
    if lowercase_error:
        feedback.append("Add at least one lowercase letter.")
    if digit_error:
        feedback.append("Add at least one number.")
    if special_error:
        feedback.append("Add at least one special character (e.g. #, @, $, %, &).")

    strong = not (length_error or uppercase_error or lowercase_error or digit_error or special_error)
    return strong, feedback

def strengthen_password(password):
    if len(password) < 8:
        password += ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=(8 - len(password))))
    if not any(ch.isupper() for ch in password):
        password += random.choice(string.ascii_uppercase)
    if not any(ch.islower() for ch in password):
        password += random.choice(string.ascii_lowercase)
    if not any(ch.isdigit() for ch in password):
        password += random.choice(string.digits)
    if not any(ch in string.punctuation for ch in password):
        password += random.choice(string.punctuation)
    password_list = list(password)
    random.shuffle(password_list)
    return ''.join(password_list)

def is_password_in_local_leak(password):
    try:
        with open(LEAK_FILE, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if line.strip() == password:
                    return True
    except FileNotFoundError:
        st.info(f"ℹ️ Local leak file '{LEAK_FILE}' not found. Create it to enable leak checks.")
    return False
if __name__ == "__main__":
    MAX_ATTEMPTS = 2   # allow only two weak attempts
    attempt = 0

    while attempt < MAX_ATTEMPTS + 1:
        user_password = input("Enter your password: ")
        strong, feedback = check_password_strength(user_password)

        if strong:
            print("✅ Your password is strong and unbreakable 🔐!")
            break
        else:
            attempt += 1

            # Local leak check
            leaked_local = is_password_in_local_leak(user_password)
            if leaked_local:
                print("❗ This password was FOUND in the local leaked-password list. Unsafe!")
            else:
                print("✅ No leak found in local file.")

            print("⚠️ Weak password detected — Feeling nervous 😰!")
            print("Suggestions:")
            for f in feedback:
                print(" -", f)

            new_password = strengthen_password(user_password)
            print("\n🔒 Suggested stronger password:", new_password)
            print()

            if attempt >= MAX_ATTEMPTS:
                print("❌ Too many weak attempts. Please try again after 1 hour.")
                # Show the real unlock time (current time + 1 hour)
                unlock_time = time.time() + COOLDOWN_SECONDS
                readable = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(unlock_time))
                print(f"⏳ You may try again after: {readable}")
                # For demo purposes we sleep a short time so program doesn't hang for an hour
                demo_sleep = 5
                print(f"(Simulating cooldown by sleeping {demo_sleep} seconds for demo; remove this in production.)")
                time.sleep(demo_sleep)
                break
            else:
                print(f"Attempt {attempt}/{MAX_ATTEMPTS} - You can try again.\n")


# ---- Streamlit UI ----
st.title("🔐 Password Strength & Leak Checker")
st.write("Check if your password is strong and safe — and whether it has appeared in a leak database.")

user_password = st.text_input("Enter your password:", type="password")

if st.button("Check Password"):
    if not user_password:
        st.warning("Please enter a password first.")
    else:
        strong, feedback = check_password_strength(user_password)
        leaked_local = is_password_in_local_leak(user_password)

        if leaked_local:
            st.error("❗ This password was found in your local leaked-password list. Unsafe!")
        else:
            st.success("✅ No leak found in local file.")

        if strong:
            st.success("✅ Your password is strong and unbreakable 🔐!")
        else:
            st.warning("⚠️ Weak password detected — Feeling nervous 😰!")
            for f in feedback:
                st.write("•", f)
            new_password = strengthen_password(user_password)
            st.info(f"🔒 Suggested stronger password: `{new_password}`")
