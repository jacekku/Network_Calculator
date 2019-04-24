import sys
import socket
import subprocess
import re


# POBIERANIE IP
def get_ip():
    if len(sys.argv) > 1:
        tmp = sys.argv[1].split("/")
        ip = tmp[0]
    else:
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        # ZAWSZE PRYWATNY
    return ip

#MASKA JAKO LICZBA
def get_mask_as_number():
    if len(sys.argv) > 1:
        tmp = sys.argv[1].split("/")
        mask_as_number = str(tmp[1])
        return mask_as_number
    else:
        ip = get_ip();
        proc = subprocess.Popen('ipconfig', stdout=subprocess.PIPE)
        while True:
            line = proc.stdout.readline()
            if str(ip).encode() in line:
                break
        mask = str(proc.stdout.readline()).rstrip().split(":")[-1].replace(' ', '')  # extracting subnet mask
        result = ip_dec_to_bin(mask[:-5])
        mask_as_number = result.count("1")
        return mask_as_number

# POBIERANIE MASKI
def get_binary_mask():
    if len(sys.argv) > 1:
        tmp = sys.argv[1].split("/")
        mask_as_number = int(tmp[1])
        mask = ""
        i = 0
        while i < mask_as_number + 3:
            if i == 8 or i == 17 or i == 26:
                mask += "."
                i += 1
            else:
                mask += "1"
                i += 1
        while i < 32 + 3:
            if i == 8 or i == 17 or i == 26:
                mask += "."
                i += 1
            else:
                mask += "0"
                i += 1

        return mask
    else:
        ip = get_ip();
        proc = subprocess.Popen('ipconfig', stdout=subprocess.PIPE)
        while True:
            line = proc.stdout.readline()
            if str(ip).encode() in line:
                break
        mask = str(proc.stdout.readline()).rstrip().split(":")[-1].replace(' ', '')  # extracting subnet mask
        result = ip_dec_to_bin(mask[:-5])
        return result


def address_correctness(ip,mask):
    # POPRAWNOSC ZNAKOWA
    characters = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.', '/']
    for i in ip:
        if i not in characters:
            return False

    # POPRAWNOSC PODZIALU
    if ip.count('.') != 3:
        return False
    for x in range(1, len(ip)):
        if ip[x] == '.' and ip[x-1] == '.':
            return False

    # POPRAWNOSC PRZEDZIALOW (0-255)
    octet_dec = ip.split(".")
    for i in range(0, 4):
        substring=octet_dec[i]
        if substring == '':
            return False
        if int(substring) < 0 or int(substring) > 255:
            return False

    # POPRAWNOSC MASKI
    if mask == "":
        return False
    if int(mask) < 0 or int(mask) > 32:
        return False

    return True

#OBLICZANIE ADRESU SIECI
def network_address(ip, mask):
    ip = ip_dec_to_bin(ip)
    mask = ip_dec_to_bin(mask)
    if len(ip) != len(mask):
        print ("Mask lenght is not equal IP lenght")
        return 0
    result = ""
    for i in range(0, len(ip)):
        if ip[i] == '.':
            result += '.'
        else:
            if ip[i] == '1' and mask[i] == '1':
                result += '1'
            else:
                result += '0'
    return ip_bin_to_dec(result)

def network_class(binary_ip):
    octet_bin=binary_ip.split(".")
    first_octet=octet_bin[0]
    if first_octet[0] == "0": return "A"
    elif first_octet[1] == "0": return "B"
    elif first_octet[2] == "0": return "C"
    elif first_octet[3] == "0": return "D"
    else: return "E"

#CZY ADRES JEST PRYWATNY
def is_private(ip):
    octet_dec = ip.split(".")
    if int(octet_dec[0]) == 10:
        if int(octet_dec[1]) >= 0 and int(octet_dec[1]) <= 255:
            if int(octet_dec[2]) >= 0 and int(octet_dec[2]) <= 255:
                if int(octet_dec[3]) >= 0 and int(octet_dec[3]) <= 255:
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False
    elif int(octet_dec[0]) == 172:
        if int(octet_dec[1]) >= 16 and int(octet_dec[1]) <= 31:
            if int(octet_dec[2]) >= 0 and int(octet_dec[2]) <= 255:
                if int(octet_dec[3]) >= 0 and int(octet_dec[3]) <= 255:
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False
    elif int(octet_dec[0])==192:
        if int(octet_dec[1])==168:
            if int(octet_dec[2])>=0 and int(octet_dec[2])<=255:
                if int(octet_dec[3])>=0 and int(octet_dec[3])<=255: return True
                else:
                     return False
            else:
               return False
        else:
            return False
    else:
        return False


#ADRES ROZGLOSZENIOWY
def broadcast_address(ip, mask):
    ip = ip_dec_to_bin(ip)
    mask = ip_dec_to_bin(mask)
    if len(ip) != len(mask):
        print ("ERROR: Incorrect usage of logical and function")
        return 0
    result = ""
    for i in range(0, len(ip)):
        if ip[i] == '.':
            result += '.'
        else:
            if mask[i] == '1':
                result += ip[i]
            else:
                result += '1'
    return ip_bin_to_dec(result)


#PIERWSZY ADRES HOSTA
def first_host_address(network_address):
    address=network_address.split('.')
    address[3]=str(int(address[3])+1)
    address=address[0]+'.'+address[1]+'.'+address[2]+'.'+address[3]
    return address

#OSTATNI ADRES HOSTA
def last_host_address(broadcast_address):
    broadcast=broadcast_address.split('.')
    broadcast[3]=str(int(broadcast[3])-1)
    broadcast=broadcast[0]+'.'+broadcast[1]+'.'+broadcast[2]+'.'+broadcast[3]
    return broadcast

#MAKSYMALNA ILOSC HOSTOW
def max_host_number(mask):
    counter = 0
    for i in range(0, len(mask), 1):
        for j in range(0, len(mask[i]), 1):
            if mask[i][j] == "1": counter += 1
    return 2**(32 - counter) - 2



# DEC na BIN
def ip_dec_to_bin(ip):
    octet_dec = ip.split(".")
    binary = ""
    for i in range(0, 3):
        binary += '{0:08b}'.format(int(octet_dec[i])) + "."
    binary += '{0:08b}'.format(int(octet_dec[3]))
    return binary


# BIN na DEC
def ip_bin_to_dec(ip):
    octet_dec = ip.split(".")
    dec_ip = ""
    for i in range (0, 3):
        num = 0
        substring = octet_dec[i]
        for j in range (0, 8):
            num += int(substring[j]) * 2 ** (7 - j)
        dec_ip += str(num) + "."
    num = 0
    substring=octet_dec[3]
    for j in range(0, 8):
        num += int(substring[j]) * 2 ** (7 - j)
    dec_ip += str(num)
    return dec_ip


ip = get_ip()
mask_as_number=get_mask_as_number()
if(address_correctness(ip,mask_as_number))==True:
    wyjscie = open("wyjscie.txt", "w")
    print("CORRECT IP ADDRESS!",file=wyjscie)
    print("Your Computer IP Adress  is: " + ip,file=wyjscie)

    binary_ip = ip_dec_to_bin(ip)
    print("Your Computer IP Adress in binary is: " + binary_ip,file=wyjscie)

    binary_mask = get_binary_mask()
    print("Your Computer IP Mask in binary is: " + binary_mask,file=wyjscie)

    mask = ip_bin_to_dec(binary_mask)
    print("Your Computer IP Mask is: " + mask,file=wyjscie)

    address = network_address(ip, mask)
    print("Your Network Adress is: " + address,file=wyjscie)

    network_class = network_class(binary_ip)
    print("Your Network Class is: " + network_class,file=wyjscie)

    if (is_private(ip) == True):
        print("Your IP Address is: private ",file=wyjscie)
    else:
        print("Your IP Address is: public ",file=wyjscie)

    broadcast = broadcast_address(ip, mask)
    print("Your Broadcast Address is: " + broadcast,file=wyjscie)

    broadcast_in_binary = ip_dec_to_bin(broadcast)
    print("Your Broadcast Address in binary is: " + broadcast_in_binary,file=wyjscie)

    first_host = first_host_address(address)
    print("First host Address is: " + first_host,file=wyjscie)

    last_host = last_host_address(broadcast)
    print("Last host Address is: " + last_host,file=wyjscie)

    first_host_in_binary = ip_dec_to_bin(first_host)
    print("First host Address in binary is: " + first_host_in_binary,file=wyjscie)

    last_host_in_binary = ip_dec_to_bin(last_host)
    print("Last host Address in binary is: " + last_host_in_binary,file=wyjscie)

    max_host = max_host_number(binary_mask)
    print("Number of host is: " + str(max_host),file=wyjscie)


else:
    print("INCORRECT IP ADDRESS",file=wyjscie)

