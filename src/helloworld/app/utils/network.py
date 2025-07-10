import socket
import platform

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  
        local_ip = s.getsockname()[0]
    except Exception as e:
        local_ip = "127.0.0.1"  
    finally:
        s.close()
    return local_ip

def get_network_cards():
    import psutil
    interfaces = psutil.net_if_addrs()  # 获取所有网络接口
    interface_stats = psutil.net_if_stats()  # 获取网络接口的状态

    network_info = []

    for interface, addresses in interfaces.items():
        # 仅考虑状态为 UP 的接口
        if interface in interface_stats and interface_stats[interface].isup:
            for addr in addresses:
                # 仅处理 IPv4 地址
                if addr.family == socket.AF_INET and addr.address not in ["127.0.0.1"]:
                    interface_info = {
                        'name': interface,
                        'addr': addr.address,
                    }
                    network_info.append(interface_info)

    return network_info

def get_local_ip_list():
    network_info = []
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  
        local_ip = s.getsockname()[0]
    except Exception as e:
        local_ip = "127.0.0.1"  
    finally:
        s.close()
    ip_info = {
        "name":"IPAdress",
        "addr":local_ip
    }
    network_info.append(ip_info)
    return network_info

def get_default_ip():
    try:
        os_name = platform.system()
        if os_name == "Windows":
            data = get_network_cards()
        else:
            data = get_local_ip_list()
        return data[0]["addr"]
    except:
        raise Exception("Failed to get default IP address") 