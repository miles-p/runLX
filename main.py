from nicegui import ui, app
import socket
from pythonosc.udp_client import SimpleUDPClient
import asyncio
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import AsyncIOOSCUDPServer
import json
import os

# Load settings from file or fall back to defaults
default_macro_commands = [
    "/eos/macro/1/fire",
    "/eos/macro/2/fire",
    "/eos/macro/3/fire",
    "/eos/macro/4/fire",
    "/eos/macro/5/fire",
]
default_console_settings = {
    "ip": "192.168.1.96",
    "tx_port": 8000,
    "rx_port": 8001,
}

settings_path = "settings.conf"

# ensure settings_path is absolute (optional, but helps avoid CWD issues)
settings_path = os.path.join(os.path.dirname(__file__), "settings.conf")

try:
    with open(settings_path, "r") as f:
        data = json.load(f)
    # load existing or fall back to defaults
    console_settings = data.get("console_settings", {}).copy() or default_console_settings.copy()
    macro_commands    = data.get("macro_commands",    [])     or default_macro_commands.copy()
    # ensure ports are ints
    console_settings["tx_port"] = int(console_settings.get("tx_port", default_console_settings["tx_port"]))
    console_settings["rx_port"] = int(console_settings.get("rx_port", default_console_settings["rx_port"]))
except (FileNotFoundError, json.JSONDecodeError):
    console_settings = default_console_settings.copy()
    macro_commands    = default_macro_commands.copy()
    # write out defaults for next time
    with open(settings_path, "w") as f:
        json.dump({
            "console_settings": console_settings,
            "macro_commands":    macro_commands
        }, f, indent=4)

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
    osc_client.send_message(f"/eos/key/{key}", 0)

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
    settings = {
        'console_settings': console_settings,
        'macro_commands': macro_commands
    }

    with open('settings.conf', 'w') as f:
        json.dump(settings, f, indent=4)

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
    osc_client.send_message("/eos/reset", 1)

ui.label("runLX Dashboard").classes('text-h3')

with ui.row():
    with ui.card().style('width: 20vw;'):
        ui.label("Connection").style('font-size: 1.2em; font-weight: bold;')
        ui.input(label="Enter Console IP", value=console_settings["ip"], on_change=lambda e: config_changed(ip=e.value, tx_port=None, rx_port=None))
        ui.input(label="Enter OSC TX Port", value=console_settings["tx_port"], on_change=lambda e: config_changed(tx_port=e.value, ip=None, rx_port=None))
        ui.input(label="Enter OSC RX Port", value=console_settings["rx_port"], on_change=lambda e: config_changed(rx_port=e.value, ip=None, tx_port=None))
        connectBox = ui.checkbox("Connect to Eos", value=False, on_change=lambda e: connect() if e.value else print("Disconnected from Eos")).classes('text-gray-500')

    with ui.card().bind_visibility_from(connectBox, 'value').style('width: 35vw;'):
        ui.label("Macro Keys").style('font-size: 1.2em; font-weight: bold;')
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
        

    with ui.column().bind_visibility_from(connectBox, 'value').style('width: 35vw;'):
        with ui.card():
            ui.label("Cue Control").style('font-size: 1.2em; font-weight: bold;')
            with ui.grid(columns=2):
                ui.button("STOP/BACK", on_click=lambda: press_key("STOP"), color="red").style('width: 100%')
                activeCueLabel = ui.label("**ACTIVE CUE**").classes('text-gray-500 font-mono')
                ui.button("GO", on_click=lambda: press_key("go_0"), color="green").style('width: 100%')
                pendingCueLabel = ui.label("**PENDING CUE**").classes('text-gray-500 font-mono')
    
    with ui.card().bind_visibility_from(connectBox, 'value'):
        ui.label("Command Line").style('font-size: 1.2em; font-weight: bold;')
        cmd_line = ui.label("**CMDLINE**").classes('text-gray-500 font-mono')

        ui.label("Keypad").style('font-size: 1.2em; font-weight: bold;')
        with ui.grid(columns=4):
            ui.button("+", color="black", on_click=lambda: press_key("+")).classes('text-white')
            ui.button("Thru", color="black", on_click=lambda: press_key("Thru")).classes('text-white')
            ui.button("-", color="black", on_click=lambda: press_key("-")).classes('text-white')
            ui.button("Sneak", color="black", on_click=lambda: press_key("Sneak")).classes('text-white')

            ui.button("7", color="black", on_click=lambda: press_key("7")).classes('text-white')
            ui.button("8", color="black", on_click=lambda: press_key("8")).classes('text-white')
            ui.button("9", color="black", on_click=lambda: press_key("9")).classes('text-white')
            ui.button("Home", color="black", on_click=lambda: press_key("Home")).classes('text-white')

            ui.button("4", color="black", on_click=lambda: press_key("4")).classes('text-white')
            ui.button("5", color="black", on_click=lambda: press_key("5")).classes('text-white')
            ui.button("6", color="black", on_click=lambda: press_key("6")).classes('text-white')
            ui.button("Out", color="black", on_click=lambda: press_key("Out")).classes('text-white')

            ui.button("1", color="black", on_click=lambda: press_key("1")).classes('text-white')
            ui.button("2", color="black", on_click=lambda: press_key("2")).classes('text-white')
            ui.button("3", color="black", on_click=lambda: press_key("3")).classes('text-white')
            ui.button("Full", color="black", on_click=lambda: press_key("Full")).classes('text-white')

            ui.button("Clear", color="black", on_click=lambda: press_key("clear_cmd")).classes('text-white')
            ui.button("0", color="black", on_click=lambda: press_key("0")).classes('text-white')
            ui.button(".", color="black", on_click=lambda: press_key(".")).classes('text-white')
            ui.button("At", color="black", on_click=lambda: press_key("At")).classes('text-white')

            ui.button("H/L", color="black", on_click=lambda: press_key("Highlight")).classes('text-white col-span-1')
            ui.button("SelAct", color="black", on_click=lambda: press_key("Select_Active")).classes('text-white col-span-1')
            ui.button("Record", color="black", on_click=lambda: press_key("Record")).classes('text-white col-span-1')
            ui.button("Group", color="black", on_click=lambda: press_key("Group")).classes('text-white col-span-1')

            ui.button("Last", color="black", on_click=lambda: press_key("Last")).classes('text-white col-span-2')
            ui.button("Next", color="black", on_click=lambda: press_key("Next")).classes('text-white col-span-2')

            ui.button("Go To Cue", color="black", on_click=lambda: press_key("go_to_cue")).classes('text-white col-span-2')
            ui.button("Enter", color="black", on_click=lambda: press_key("Enter")).classes('text-white col-span-2')
    
    with ui.card().bind_visibility_from(connectBox, 'value'):
        ui.label("About").style('font-size: 1.2em; font-weight: bold;')
        ui.label("Show File:")
        file_name = ui.label("**FILENAME**").classes('text-gray-500 font-mono')

            
def osc_callback(address, *args):
    print("UPDATING CMDLINE")
    if address == "/eos/out/cmd":
        cmd_line.set_text(args[0] if args else "No arguments received")
        cmd_line.update()
    if address == "/eos/out/show/name":
        file_name.set_text(args[0] if args else "No show file name received")
        file_name.update()
    if address == "/eos/out/active/cue/text":
        activeCueLabel.set_text(args[0] if args else "No active cue text received")
        activeCueLabel.update()
    if address == "/eos/out/pending/cue/text":
        pendingCueLabel.set_text(args[0] if args else "No pending cue text received")
        pendingCueLabel.update()
    print(f"Received OSC message: {address} with args: {args}")

async def start_osc_receiver():
    dispatcher = Dispatcher()
    dispatcher.map("/eos/*", osc_callback)
    server = AsyncIOOSCUDPServer(
        (console_settings['ip'], console_settings['rx_port']),
        dispatcher,
        asyncio.get_event_loop()
    )
    await server.create_serve_endpoint()
    print(f"OSC Receiver started on {console_settings['ip']}:{console_settings['rx_port']}")

app.on_startup(start_osc_receiver)
loop = asyncio.get_event_loop()
ui.run(title="runLX Dashboard", port=8080, dark=True, reload=True)