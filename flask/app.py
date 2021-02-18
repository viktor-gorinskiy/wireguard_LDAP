from flask import Flask, render_template
import sys
import telnetlib

sys.path.append('../')
import wg_lib as wg

app = Flask(__name__)

def get_peers():
    peers = []

    peers_status = wg.wireguard(action='status')
    for status in peers_status.items():
        peer = status[0]
        endpoint = status[1]['endpoint']
        handshake = status[1]['handshake'].replace('_', ' ')
        allowed_ips = status[1]['allowed_ips']

        peer_name = 'system_peer'

        peer_search_in_file = wg.find_in_file(peer_pub_key=peer)

        if peer_search_in_file:
            peer_name = peer_search_in_file['name']
            # print('peer_name==> ', peer_name)
        peer_data = {}
        if endpoint:
            peer_data['peer_name'] = peer_name
            peer_data['peer'] = peer
            peer_data['endpoint'] = endpoint
            peer_data['handshake'] = handshake
            peer_data['allowed_ips'] = allowed_ips
            peers.append(peer_data)
    return peers

def get_openvpn():
    host = '127.0.0.1'
    port = 5555

    telnet = telnetlib.Telnet()

    telnet.open(host, port)

    telnet.write(b'status\r\n')
    peers_src = telnet.read_until(b'END').decode("utf-8").split('\r\n')

    peers = []
    for peer_src in peers_src:

        peer_src = peer_src.split(',')
        if peer_src[0] == 'CLIENT_LIST':
            peer_data = {}

            peer_name = peer_src[9]
            ip_ext = peer_src[2].split(':')[0]
            ip_int = peer_src[3]
            peer_data['peer_name'] = peer_name
            peer_data['ip_ext'] = ip_ext
            peer_data['ip_int'] = ip_int
            # peer[peer_src[1]] = peer
            # peer[peer_src[1]]['ip_ext'] =  peer_src[2]
            # peer[peer_src[1]]['ip_int'] =  peer_src[3]
            peers.append(peer_data)

    return peers

# for a in get_peers():
#     print(a)
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/openvpn')
def openvpn():
    peers = get_openvpn()
    return render_template('openvpn.html', peers=peers)

@app.route('/wireguard')
def wireguard():
    peers = get_peers()
    return render_template('wireguard.html', peers=peers)
#
# if __name__ == '__main__':
#     app.run('127.0.0.1', '5000')