# import pymodbus
from pymodbus.client import ModbusTcpClient

def read_modbus_registers(ip_address, port, unit_id, start_address, quantity):
  """Reads Modbus registers from a TCP device.

  Args:
    ip_address: The IP address of the Modbus device.
    port: The port number of the Modbus device (usually 502).
    unit_id: The unit ID of the Modbus device.
    start_address: The starting address of the registers to read.
    quantity: The number of registers to read.

  Returns:
    A list of register values.
  """

  client = ModbusTcpClient(ip_address, port=port)

  try:
    if client.connect():
      # result = client.read_holding_registers(start_address, quantity, unit=unit_id)
      result = client.read_holding_registers(start_address, quantity)
      if result.isError():
        print(f"Error reading registers: {result}")
        return None
      else:
        return result.registers
    else:
      print("Connection failed")
      return None
  finally:
    client.close()

# Example usage:
ip_address = "192.168.100.67"
port = 502
unit_id = 1
start_address = 0
quantity = 38

registers = read_modbus_registers(ip_address, port, unit_id, start_address, quantity)

if registers:
  print(registers)
