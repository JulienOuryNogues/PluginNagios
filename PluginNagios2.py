from __future__ import division
import os
import sys
import time


def get_somme(address,octin=True,octout=True):
    """
    :param address: The address of the machine to monitor
    :param octin: Request all the octets in
    :param octout: Request all the octets out
    :return: The sum of all the octets requested
    """
    res=0
    #First retrieve the number of network interfaces
    cmd_nombre_interfaces = "snmpget -v1 -c public -Ovqn " + address + " 1.3.6.1.2.1.2.1.0"
    Ninterfaces=int(os.popen(cmd_nombre_interfaces).read())
    if (octin):
        cmd_octets_in="snmpget -v1 -c public -Ovqn " + address +" 1.3.6.1.2.1.2.2.1.10."
        for i in range(1,Ninterfaces+1):
            res+=int(os.popen(cmd_octets_in+str(i)).read())
    if (octout):
        cmd_octets_out="snmpget -v1 -c public -Ovqn " + address +" 1.3.6.1.2.1.2.2.1.16."
        for i in range(1,Ninterfaces+1):
            res+=int(os.popen(cmd_octets_out+str(i)).read())
    return res

def get_time(address):
    """
    :param address: The address of the machine to monitor
    :return: Return the time clock
    """
    cmd_time="snmpget -v1 -c  public -Ovqnt "+address+" 1.3.6.1.2.1.1.3.0"
    return int(os.popen(cmd_time).read())

def get_variation(address,octin=True,octout=True):
    """
    :param address: The address of the machine to monitor
    :param octin: Request all the octets in
    :param octout: Request all the octets out
    :return: The variations of octets requested
    """
    res = get_somme(address, in_request, out_request)
    time1=get_time(address)
    time.sleep(globalDelay)
    res -= get_somme(address, in_request, out_request)
    time2=get_time(address)
    res /= (time1-time2)
    return res

def get_args(args):
    """
    :param args: list of all arguments given to the script
    :return: Argument of the function if specified in the command
    """
    i=1
    limit_crit = float("inf")
    limit_warning = float("inf")
    address="localhost"
    in_request=False
    out_request=False
    delay=False
    while (i < len(args)):
        if args[i] == "-a":
            address=str(args[i+1])
            i+=2
            continue
        if args[i] == "-c":
            limit_crit = int(args[i + 1])
            i += 2
            continue
        if args[i]=="-d" or args[i]=="--delta":
            delay=True
            i+=1
            continue
        if args[i] == "-i":
            in_request=True
            i+=1
            continue
        if args[i] =="-o":
            out_request=True
            i+=1
            continue
        if args[i] == "-w":
            limit_warning = int(args[i + 1])
            i += 2
            continue
        else:
            print("Argument %s not in list. Ignored " % args[i])
            i+=1
            continue
    return(address,limit_warning,limit_crit,in_request,out_request,delay)

def help():
    """
    Displays all informations about the plugin
    """
    print("")
    print("This plugin gives you informations about Ethernet's packet received and transmitted. ")
    print("By default, calculate the weight of all Ethernet's packets in and out ")
    print(" Options  : ")
    print("     -a [string] : By default 'localhost'. Choose the ip adress to monitor ")
    print("     -c [number] : In octets. If the result is above, returns a critical Status")
    print("     -d or --delta : Changes the result of the plugin : ")
    print("          Variation of average weight of all Ethernet's packets in and out. ")
    print("          (Be sure to choose correctly -w and -c levels instead")
    print("     -h or --help : Displays the help menu")
    print("     -i : Calculate for all in packets (by default calculate both in and out)")
    print("     -o : Calculate for all out packets (by default calculate both in and out)")
    print("     -w [number] : In octets. If the result is above (and below c), returns a warning Status")





if __name__=="__main__":
    globalDelay=float(0.1)
    args=sys.argv
    if '-h' in args or '--help' in args:
        help()
        sys.exit(0)
    try:
        (address,limit_warning,limit_crit,in_request,out_request,delay)=get_args(args)
    except:
        print("SYNTAX ERROR. Please see the help (-h or --help)")
        sys.exit(2)

    if in_request==out_request:
        in_request=True
        out_request=True
        info="all"
    if in_request and not(out_request):
        info="only 'in'"
    if out_request and not(in_request):
        info="only 'out'"

    if not(delay):
        somme = get_somme(address,in_request,out_request)
        if somme>=limit_crit:
            print("SNMP CRITICAL - Weight of %s Ethernet's packets : %d octets" % (info,somme))
            sys.exit(2)
        elif somme>=limit_warning:
            print("SNMP WARNING - Weight of %s Ethernet's packets : %d octets" % (info,somme))
            sys.exit(1)
        else:
            print("SNMP OK - Weight of %s Ethernet's packets  : %d octets" % (info,somme))
            sys.exit(0)
    else:
        variation=get_variation(address,in_request,out_request)
        if variation>=limit_crit:
            print("SNMP CRITICAL - Variation of weight of %s Ethernet's packets  : %d octets" % (info,variation))
            sys.exit(2)
        elif variation>=limit_warning:
            print("SNMP WARNING - Variation of weight of %s Ethernet's packets  : %d octets" % (info,variation))
            sys.exit(1)
        else:
            print("SNMP OK - Variation of weight of %s Ethernet's packets  : %d octets" % (info,variation))
            sys.exit(0)
