import subprocess
import sys
import time

def run_cmd(command):
    """Executes a Termux:API command and returns the output."""
    try:
        print(f"[*] Executing: {command}")
        result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        return result.decode('utf-8').strip()
    except subprocess.CalledProcessError as e:
        return f"[!] Error executing command: {e.output.decode('utf-8').strip()}"

def generate_menu():
    print("\n" + "="*40)
    print("      OPENDROIDBOT (Local Version)")
    print("="*40)
    print("Select a hardware action:")
    print("1. Check Battery Status")
    print("2. Vibrate Phone (1 second)")
    print("3. Turn Flashlight ON")
    print("4. Turn Flashlight OFF")
    print("5. Open a Website in Browser")
    print("6. Show Device Info")
    print("0. Exit")
    print("="*40)

def main():
    while True:
        generate_menu()
        choice = input("Enter your choice (0-6): ")

        if choice == '1':
            output = run_cmd("termux-battery-status")
            print("\n--- Battery Info ---")
            print(output)
            
        elif choice == '2':
            print("\n--- Vibrating ---")
            run_cmd("termux-vibrate -f -d 1000")
            print("Done.")

        elif choice == '3':
            print("\n--- Flashlight ON ---")
            run_cmd("termux-torch on")

        elif choice == '4':
            print("\n--- Flashlight OFF ---")
            run_cmd("termux-torch off")

        elif choice == '5':
            url = input("Enter URL (e.g., https://google.com): ")
            if not url.startswith("http"):
                url = "https://" + url
            print(f"\n--- Opening {url} ---")
            run_cmd(f"termux-open-url {url}")
            
        elif choice == '6':
            print("\n--- Device Info ---")
            info = run_cmd("termux-telephony-deviceinfo")
            print(info)

        elif choice == '0':
            print("\nExiting OpenDroidBot. Goodbye!")
            sys.exit(0)
            
        else:
            print("\n[!] Invalid choice. Please try again.")

        time.sleep(1)

if __name__ == "__main__":
    main()
