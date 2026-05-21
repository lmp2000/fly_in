from src.parser.map_parser import MapParser


parser = MapParser()
map_data = parser.parse_file("maps/phase1_valid.txt")

print("Number of drones:", map_data.nb_drones)
print("Start:", map_data.start_name)
print("End:", map_data.end_name)

print("\nZones:")
for zone_name, zone in map_data.zones.items():
    print(zone_name, zone)

print("\nConnections:")
for connection in map_data.connections:
    print(connection)
