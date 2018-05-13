from __future__ import division
import os
import sys
import time


def get_mean(address):
    """
    :param address: The address of the machine to monitor
    :return: Average weight of Ethernet's packet received
    """
    cmd_nombre_octets_recus="snmpget -v1 -c public -Ovqn "+address+" 1.3.6.1.2.1.2.2.1.10.2"
    i=11 #Unicast Packets
    cmd_nombre_paquets_recus="snmpget -v1 -c public -Ovqn "+address+" 1.3.6.1.2.1.2.2.1."+str(i)+".2"
    Nb_Octets=int(os.popen(cmd_nombre_octets_recus).read())
    Nb_Paquets=int(os.popen(cmd_nombre_paquets_recus).read())
    i+=1 #Non Unicast Packet
    cmd_nombre_paquets_recus = "snmpget -v1 -c public -Ovqn "+address+" 1.3.6.1.2.1.2.2.1." + str(i) + ".2"
    Nb_Paquets+=int(os.popen(cmd_nombre_paquets_recus).read())
    return Nb_Octets//Nb_Paquets

def get_time(address):
    """
    :param address: The address of the machine to monitor
    :return: Return the time clock
    """
    cmd_time="snmpget -v1 -c  public -Ovqnt "+address+" 1.3.6.1.2.1.1.3.0"
    return int(os.popen(cmd_time).read())


def get_variation(address):
    """
    :param address: The address of the machine to monitor
    :return: Variation of average weight of all Ethernet's packet received
    """
    res = get_mean(address)
    time1 = get_time(address)
    time.sleep(globalDelay)
    res -= get_mean(address)
    time2 = get_time(address)
    res /= (time1 - time2)
    return res



def get_args(args):
    """
    :param args: list of all arguments given to the script
    :return: Argument of the function if specified in the command
    """
    i=1
    limit_crit = float("inf")
    limit_warning = float("inf")
    delay = False
    address="localhost"
    while (i < len(args)):
        if args[i] == "-a":
            address=str(args[i+1])
            i+=2
            continue
        if args[i] == "-c":
            limit_crit = int(args[i + 1])
            i += 2
            continue
        if args[i] == "-d" or args[i] == "--delta":
            delay = True
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
    return(address,delay,limit_warning,limit_crit)

def help():
    """
    Displays all informations about the plugin
    """
    print("")
    print("This plugin gives you informations about Ethernet's packet received. ")
    print("By default, calculate the average weight of all Ethernet's packet received ")
    print(" Options  : ")
    print("     -a [string] : By default 'localhost'. Choose the ip adress to monitor ")
    print("     -c [number] : In octets. If the result is above, returns a critical Status")
    print("     -d or --delta : Changes the result of the plugin : ")
    print("          Variation of average weight of all Ethernet's packet received. ")
    print("          (Be sure to choose correctly -w and -c levels instead")
    print("     -h or --help : Displays the help menu")
    print("     -w [number] : In octets. If the result is above (and below c), returns a warning Status")


if __name__=="__main__":
    globalDelay=float(0.1)
    args=sys.argv
    if '-h' in args or '--help' in args:
        help()
        sys.exit(0)
    try:
        (address,delay,limit_warning,limit_crit)=get_args(args)
    except:
        print("SYNTAX ERROR. Please see the help (-h or --help)")
        sys.exit(2)
    if not(delay):
        moyenne = get_mean(address)
        if moyenne>=limit_crit:
            print("SNMP CRITICAL - Average weight of all Ethernet's packet received : %d octets" % moyenne)
            sys.exit(2)
        elif moyenne>=limit_warning:
            print("SNMP WARNING - Average weight of all Ethernet's packet received : %d octets" % moyenne)
            sys.exit(1)
        else:
            print("SNMP OK - Average weight of all Ethernet's packet received : %d octets" % moyenne)
            sys.exit(0)
    else:
        variation=get_variation(address)
        if variation>=limit_crit:
            print("SNMP CRITICAL - Variation of average weight of all Ethernet's packet received : %d octets" % variation)
            sys.exit(2)
        elif variation>=limit_warning:
            print("SNMP WARNING - Variation of average weight of all Ethernet's packet received : %d octets" % variation)
            sys.exit(1)
        else:
            print("SNMP OK - Variation of average weight of all Ethernet's packet received : %d octets" % variation)
            sys.exit(0)
