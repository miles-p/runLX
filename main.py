from nicegui import ui
import socket
import pythonosc
from pythonosc.udp_client import SimpleUDPClient

macro_commands = ["/eos/macro/1/fire",
                  "/eos/macro/2/fire",
                  "/eos/macro/3/fire",
                  "/eos/macro/4/fire",
                  "/eos/macro/5/fire"]

console_settings = {
    'ip': '127.0.0.1',
    'tx_port': 8000,
    'rx_port': 8001}

def send_osc(address: str, *args):
    """
    Send an OSC message to the configured host.
    address: OSC address pattern, e.g. "/eos/cue/go"
    *args: any values to send
    """
    osc_client.send_message(address, list(args))

def press_key(key: str):
    """
    Simulate a key press.
    key: The key to press, e.g. "BACK" or "GO"
    """
    print(f"Simulating key press: {key}")
    # Here you would typically use a library like pynput to simulate the key press
    # For example: keyboard.press_and_release(key)
    osc_client.send_message(f"/eos/key/{key}", 1)

def get_local_ips():
    hostname = socket.gethostname()
    infos = socket.getaddrinfo(hostname, None)
    ips = []
    for family, *_ , sockaddr in infos:
        if family == socket.AF_INET:
            ip = sockaddr[0]
            if not ip.startswith("127.") and ip not in ips:
                ips.append(ip)
    return ips

def macro_changed(macro_number: int, value: str):
    """
    Handle changes to macro input fields.
    macro_number: The number of the macro being changed (1-4)
    value: The new OSC address for the macro
    """
    print(f"Macro {macro_number} changed to: {value}")
    # Update the macro_commands list with the new value
    if 1 <= macro_number <= len(macro_commands):
        macro_commands[macro_number - 1] = value
    # Here you would typically update the OSC client or configuration

def config_changed( ip: str, tx_port: int, rx_port: int):
    """
    Handle changes to the console configuration.
    ip: The new IP address of the console
    tx_port: The new OSC transmit port
    rx_port: The new OSC receive port
    """
    if ip: console_settings['ip'] = ip
    if tx_port: console_settings['tx_port'] = tx_port
    if rx_port: console_settings['rx_port'] = rx_port
    print(f"Configuration changed: {console_settings}")

def connect():
    """
    Connect to the Eos console using the configured settings.
    This function would typically set up the OSC client with the provided IP and ports.
    """
    print("Connecting to Eos console...")
    # Here you would typically set the IP and ports for the OSC client
    # osc_client = SimpleUDPClient(console_ip, tx_port)
    global osc_client
    osc_client = SimpleUDPClient(console_settings['ip'], console_settings['tx_port'])

connect()

ui.label("runLX Dashboard").classes('text-h3')

with ui.row():
    with ui.card():
        ui.label("Connection")
        ui.select(get_local_ips(), label="Network Interface", value=get_local_ips()[0] if get_local_ips() else None, on_change=lambda e: print(f"IP Address changed to: {e.value}"))
        ui.input(label="Enter Console IP", value="0.0.0.0", on_change=lambda e: config_changed(e.value, console_settings['tx_port'], console_settings['rx_port']))
        ui.input(label="Enter OSC TX Port", value="8000", on_change=lambda e: config_changed(console_settings['ip'], e.value, console_settings['rx_port']))
        ui.input(label="Enter OSC RX Port", value="8001", on_change=lambda e: config_changed(e.value, console_settings['tx_port'], console_settings['rx_port']))
        ui.button("Connect", on_click=connect, color="gray")

    with ui.card():
        ui.label("Macro Keys")
        with ui.row():
            ui.button("Macro 1", on_click=lambda: send_osc(macro_commands[0]), color="gray")
            ui.input(label="OSC for Macro 1", value=macro_commands[0], on_change=lambda e: macro_changed(1, e.value))
        with ui.row():
            ui.button("Macro 2", on_click=lambda: send_osc(macro_commands[1]), color="gray")
            ui.input(label="OSC for Macro 2", value=macro_commands[1], on_change=lambda e: macro_changed(2, e.value))
        with ui.row():
            ui.button("Macro 3", on_click=lambda: send_osc(macro_commands[2]), color="gray")
            ui.input(label="OSC for Macro 3", value=macro_commands[2], on_change=lambda e: macro_changed(3, e.value))
        with ui.row():
            ui.button("Macro 4", on_click=lambda: send_osc(macro_commands[3]), color="gray")
            ui.input(label="OSC for Macro 4", value=macro_commands[3], on_change=lambda e: macro_changed(4, e.value))
        with ui.row():
            ui.button("Macro 5", on_click=lambda: send_osc(macro_commands[4]), color="gray")
            ui.input(label="OSC for Macro 5", value=macro_commands[4], on_change=lambda e: macro_changed(5, e.value))
        

    with ui.column():
        with ui.card():
            ui.label("Cue Functionality")
            ui.checkbox('Enable Cue Go/Back', value=True, on_change=lambda e: print(f"Cue Functionality enabled: {e.value}"))

        with ui.card():
            ui.label("Manual Cue Control")
            ui.button("BACK", on_click=lambda: press_key("STOP"), color="red")
            ui.button("GO", on_click=lambda: press_key("go_0"), color="green")
            
            
ui.run(title="runLX", port=8080, dark=True)