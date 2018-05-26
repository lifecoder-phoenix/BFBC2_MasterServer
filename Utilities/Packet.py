from ConfigParser import ConfigParser

from struct import pack


class Packet(object):
    def __init__(self, packet_data):
        self.packet_data = packet_data

    def generateChecksum(self, packet_id, PacketCount):
        PacketID = self.generatePacketID(packet_id + PacketCount)
        PacketLength = self.generatePacketLength()

        return PacketID + PacketLength

    def generatePacketID(self, packet_id):
        return pack(">I", packet_id)

    def generatePacketLength(self):
        return pack(">I", len(self.packet_data) + 12)

    def verifyPacketLength(self, packet_length):
        data_len = pack(">I", len(self.packet_data))

        if data_len == packet_length:
            return True
        else:
            return False

    def dataInterpreter(self):
        data = self.packet_data.split("\n")
        data.remove('\x00')  # Remove NULL from data

        dataObj = ConfigParser()
        dataObj.optionxform = str

        dataObj.add_section("PacketData")  # Will save all packet data to PacketData section

        for entry in data:
            parameter = entry.split("=", 1)[0]
            value = entry.split("=", 1)[1]

            dataObj.set("PacketData", parameter, value)

        return dataObj

    def generatePacket(self, packet_type, packet_id, PacketCount):
        packetData = self.packet_data.items("PacketData")

        self.packet_data = ""

        for entry in packetData:
            parameter = entry[0]
            value = entry[1]

            try:
                if value.find(" ") != -1:
                    self.packet_data += parameter + "=" + '"' + str(value) + '"' + "\n"
                else:
                    self.packet_data += parameter + "=" + str(value) + "\n"
            except AttributeError:
                self.packet_data += parameter + "=" + str(value) + "\n"

        self.packet_data = self.packet_data[:-1]
        self.packet_data += "\x00"


        newPacket = packet_type

        newPacket += self.generateChecksum(packet_id, PacketCount)

        newPacket += self.packet_data
        return newPacket