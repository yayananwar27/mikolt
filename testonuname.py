#show onu-type
data = """
ONU type name:          ZTE-F601
PON type:               gpon
Description:            1ETH
Max T-CONT:             8
Max GEM port:           32
Max switch per slot:    8
Max flow per switch:    8
Max IP host:            2
Max IPv6 host:          0
Service ability N:1:    support
Service ability 1:M:    support
Service ability 1:P:    support
WIFI mgmt via non OMCI: disable
OMCI send mode:         async
Default multicast range:none
VRG:                    disable
MGC configure mode:     zte
Max VEIP:               0(default: 1 VEIP)
Extended OMCI:          disable
Location:               disable

ONU type name:          ZTE-F609
PON type:               gpon
Description:            4ETH,2POTS,WIFI
Max T-CONT:             7
Max GEM port:           32
Max switch per slot:    8
Max flow per switch:    32
Max IP host:            5
Max IPv6 host:          0
Service ability N:1:    support
Service ability 1:M:    support
Service ability 1:P:    support
WIFI mgmt via non OMCI: enable
OMCI send mode:         async
Default multicast range:none
VRG:                    disable
MGC configure mode:     zte
Max VEIP:               0(default: 1 VEIP)
Extended OMCI:          disable
Location:               disable

ONU type name:          ZTE-F621
PON type:               gpon
Description:            6ETH, 4E1
Max T-CONT:             8
Max GEM port:           32
Max switch per slot:    8
Max flow per switch:    8
Max IP host:            2
Max IPv6 host:          0
Service ability N:1:    support
Service ability 1:M:    support
Service ability 1:P:    support
WIFI mgmt via non OMCI: disable
OMCI send mode:         async
Default multicast range:none
VRG:                    disable
MGC configure mode:     zte
Max VEIP:               0(default: 1 VEIP)
Extended OMCI:          disable
Location:               disable

ONU type name:          ZTE-F622
PON type:               gpon
Description:            4ETH, 2POTS
Max T-CONT:             8
Max GEM port:           32
Max switch per slot:    8
Max flow per switch:    8
Max IP host:            2
Max IPv6 host:          0
Service ability N:1:    support
Service ability 1:M:    support
Service ability 1:P:    support
WIFI mgmt via non OMCI: disable
OMCI send mode:         async
Default multicast range:none
VRG:                    disable
MGC configure mode:     zte
Max VEIP:               0(default: 1 VEIP)
Extended OMCI:          disable
Location:               disable

ONU type name:          ZTE-F625
PON type:               gpon
Description:            4ETH, 2POTS, 1RF
Max T-CONT:             8
Max GEM port:           32
Max switch per slot:    8
Max flow per switch:    8
Max IP host:            2
Max IPv6 host:          0
Service ability N:1:    support
Service ability 1:M:    support
Service ability 1:P:    support
WIFI mgmt via non OMCI: disable
OMCI send mode:         async
Default multicast range:none
VRG:                    disable
MGC configure mode:     zte
Max VEIP:               0(default: 1 VEIP)
Extended OMCI:          disable
Location:               disable

ONU type name:          ZTE-F628
PON type:               gpon
Description:            6ETH, 2POTS, 1RF, 1WiFi
Max T-CONT:             7
Max GEM port:           32
Max switch per slot:    32
Max flow per switch:    8
Max IP host:            2
Max IPv6 host:          0
Service ability N:1:    support
Service ability 1:M:    support
Service ability 1:P:    support
WIFI mgmt via non OMCI: disable
OMCI send mode:         async
Default multicast range:none
VRG:                    disable
MGC configure mode:     zte
Max VEIP:               0(default: 1 VEIP)
Extended OMCI:          disable
Location:               disable

ONU type name:          ZTE-F640
PON type:               gpon
Description:            1ETH, 2POTS, 1RF
Max T-CONT:             8
Max GEM port:           32
Max switch per slot:    8
Max flow per switch:    8
Max IP host:            2
Max IPv6 host:          0
Service ability N:1:    support
Service ability 1:M:    support
Service ability 1:P:    support
WIFI mgmt via non OMCI: disable
OMCI send mode:         async
Default multicast range:none
VRG:                    disable
MGC configure mode:     zte
Max VEIP:               0(default: 1 VEIP)
Extended OMCI:          disable
Location:               disable

ONU type name:          ZTE-F641
PON type:               gpon
Description:            4ETH
Max T-CONT:             8
Max GEM port:           32
Max switch per slot:    8
Max flow per switch:    8
Max IP host:            2
Max IPv6 host:          0
Service ability N:1:    support
Service ability 1:M:    support
Service ability 1:P:    support
WIFI mgmt via non OMCI: disable
OMCI send mode:         async
Default multicast range:none
VRG:                    disable
MGC configure mode:     zte
Max VEIP:               0(default: 1 VEIP)
Extended OMCI:          disable
Location:               disable
"""

# Extract ONU type names and create a list
onu_type_names = [line.split(":")[1].strip() for line in data.splitlines() if line.startswith("ONU type name")]

print(onu_type_names)
