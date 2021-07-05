from pysnmp.hlapi import *
import pysnmp
import json
import time

def snmpData(community, ip, port, oid):

    iterator = getCmd(SnmpEngine(),
                      CommunityData(community),
                      UdpTransportTarget((ip, port)),
                      ContextData(),
                      ObjectType(ObjectIdentity(tuple(map(int, oid.split('.')))))
                )

    errorIndication, errorStatus, errorIndex, varBinds = next(iterator)
    
    if errorIndication:  # SNMP engine errors
        print(errorIndication)
        snmpValue = "0"
    else:
        if errorStatus:  # SNMP agent errors
            print('%s at %s' % (errorStatus.prettyPrint(), varBinds[int(errorIndex)-1] if errorIndex else '?'))
            snmpValue = "0"
        else:
            for varBind in varBinds:  # SNMP response contents
                snmpValue = str(varBind).split(' = ')[1]
                print(' = '.join([x.prettyPrint() for x in varBind]))            

    return snmpValue
    
    
def lambda_handler(event, context):
    
    curTime = int(round(time.time() * 1000))

    lanInput = snmpData("COMMUNITY","198.51.100.84",161, "1.3.6.1.2.1.2.2.1.10.1")
    lanOutput = snmpData("COMMUNITY","198.51.100.84",161, "1.3.6.1.2.1.2.2.1.16.1")
    wanInput = snmpData("COMMUNITY","198.51.100.84",161, "1.3.6.1.2.1.2.2.1.10.6")
    wanOutput = snmpData("COMMUNITY","198.51.100.84",161, "1.3.6.1.2.1.2.2.1.16.6")
    lanBgpStatus = snmpData("COMMUNITY","198.51.100.84",161, "1.3.6.1.2.1.15.3.1.2.198.51.100.4")
    wanBgpStatus = snmpData("COMMUNITY","198.51.100.84",161, "1.3.6.1.2.1.15.3.1.2.203.0.113.17")
 
    # DADOS INTERFACE LAN ROUTER SP/PARTNER
    print('{"_aws": {"Timestamp":' + str(curTime) + ',"CloudWatchMetrics": [{"Namespace": "service-mon","Dimensions": [["Link Usage"]],"Metrics": [{"Name":"Interface ifInOctets","Unit": "Bits"}]}]},"Link Usage": "SP Interface SNMP ifInOctets","Interface ifInOctets": ' + str(lanInput) +  '}')
    print('{"_aws": {"Timestamp":' + str(curTime) + ',"CloudWatchMetrics": [{"Namespace": "service-mon","Dimensions": [["Link Usage"]],"Metrics": [{"Name":"Interface ifOutOctets","Unit": "Bits"}]}]},"Link Usage": "SP Interface SNMP ifOutOctets","Interface ifOutOctets": ' + str(lanOutput) +  '}')  

    # DADOS INTERFACE WAN ROUTER SP/PARTNER
    print('{"_aws": {"Timestamp":' + str(curTime) + ',"CloudWatchMetrics": [{"Namespace": "service-mon","Dimensions": [["Link Usage"]],"Metrics": [{"Name":"Interface ifInOctets","Unit": "Bits"}]}]},"Link Usage": "Partner Interface SNMP ifInOctets","Interface ifInOctets": ' + str(wanInput) +  '}')
    print('{"_aws": {"Timestamp":' + str(curTime) + ',"CloudWatchMetrics": [{"Namespace": "service-mon","Dimensions": [["Link Usage"]],"Metrics": [{"Name":"Interface ifOutOctets","Unit": "Bits"}]}]},"Link Usage": "Partner Interface SNMP ifOutOctets","Interface ifOutOctets": ' + str(wanOutput) +  '}')       

    #STATUS SESSÃO BGP INTERFACE LAN
    print('{"_aws": {"Timestamp":' + str(curTime) + ',"CloudWatchMetrics": [{"Namespace": "service-mon","Dimensions": [["BGP"]],"Metrics": [{"Name":"BGP Status","Unit": "Count"}]}]},"BGP": "LAN BGP Session Status","BGP Status": ' + str(lanBgpStatus) +  '}')

    #STATUS SESSÃO BGP INTERFACE WAN
    print('{"_aws": {"Timestamp":' + str(curTime) + ',"CloudWatchMetrics": [{"Namespace": "service-mon","Dimensions": [["BGP"]],"Metrics": [{"Name":"BGP Status","Unit": "Count"}]}]},"BGP": "WAN BGP Session Status","BGP Status": ' + str(wanBgpStatus) +  '}')

    return { 
        'body': json.dumps('Metrics Successfully Collected!')
    }
