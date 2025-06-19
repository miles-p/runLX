from nicegui import ui
import socket
import pythonosc
from pythonosc.udp_client import SimpleUDPClient

# initialize a Python OSC client (replace IP and port as needed)
osc_client = SimpleUDPClient('127.0.0.1', 8000)

macro_commands = ["/eos/macro/1/fire",
                  "/eos/macro/2/fire",
                  "/eos/macro/3/fire",
                  "/eos/macro/4/fire",
                  "/eos/macro/5/fire"]

def send_osc(address: str, *args):
    """
    Send an OSC message to the configured host.
    address: OSC address pattern, e.g. "/eos/cue/go"
    *args: any values to send
    """
    osc_client.send_message(address, list(args))

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

def cue_go():
    """
    Send an OSC message to trigger the 'go' action for cues.
    """
    send_osc("/eos/key/go_0", 1)
    print("GO button clicked")

ui.label("Eos Keyboard Configuration")

with ui.row():
    with ui.card():
        ui.label("Basics")
        ui.select(get_local_ips(), label="IP Address", value=get_local_ips()[0] if get_local_ips() else None, on_change=lambda e: print(f"IP Address changed to: {e.value}"))
        ui.input(label="Enter OSC TX Port", value="8000", on_change=lambda e: print(f"TX Port changed to: {e.value}"))
        ui.input(label="Enter OSC RX Port", value="8001", on_change=lambda e: print(f"RX Port changed to: {e.value}"))

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
            ui.button("BACK", on_click=lambda: print("BACK button clicked"), color="red")
            ui.button("GO", on_click=cue_go, color="green")
ui.run(title="Eos Keyboard Config", port=8080, dark=True)