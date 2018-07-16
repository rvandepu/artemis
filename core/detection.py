import radix
from webapp import app
from webapp.data.models import Hijack, Monitor, db
import _thread
from multiprocessing import Queue
from sqlalchemy import and_, exc, desc
import traceback
from core import exception_handler
import ipaddress

class Detection():

    def __init__(self, confparser):
        self.confparser = confparser
        self.monitor_queue = Queue()
        self.prefix_tree = radix.Radix()
        self.flag = False

    def __detection_generator(self):
        yield self.detect_origin_hijack
        yield self.detect_type_1_hijack
        yield self.detect_subprefix_hijack
        yield self.mark_handled

    def init_detection(self):
        configs = self.confparser.get_obj()
        for config in configs:
            for prefix in configs[config]['prefixes']:
                node = self.prefix_tree.add(str(prefix))
                node.data['origin_asns'] = configs[config]['origin_asns']
                node.data['neighbors'] = configs[config]['neighbors']

    def start(self):
        if not self.flag:
            self.flag = True
            _thread.start_new_thread(self.parse_queue, ())

    def stop(self):
        if self.flag:
            self.flag = False
            self.monitor_queue.put(None)

    def parse_queue(self):
        with app.app_context():
            print('[+] Detection Mechanism Started..')
            self.init_detection()

            unhandled_events = Monitor.query.filter_by(handled=False).all()

            @exception_handler
            def handle_monitor_event(monitor_event):
                if monitor_event is None:
                    return

                # ignore withdrawals for now
                if monitor_event.type == 'W':
                    monitor_event.handled = True
                    db.session.commit()
                    return

                for func in self.__detection_generator():
                    if func(monitor_event):
                        break

            for monitor_event in unhandled_events:
                handle_monitor_event(monitor_event)

            while self.flag:
                monitor_event = self.monitor_queue.get()
                handle_monitor_event(monitor_event)
            print('[+] Detection Mechanism Stopped..')

    def commit_hijack(self, monitor_event, origin, hij_type):
        # Trigger hijack
        hijack_event = Hijack.query.filter(
            and_(
                Hijack.type.like(str(hij_type)),
                Hijack.prefix.like(monitor_event.prefix),
                Hijack.hijack_as.like(origin)
            )
        ).order_by(desc(Hijack.id)).first()

        if hijack_event is None or hijack_event.time_ended is not None:
            hijack = Hijack(monitor_event, origin, str(hij_type))
            db.session.add(hijack)
            db.session.commit()
            hijack_id = hijack.id
            print('[DETECTION] NEW TYPE {} HIJACK!\n{}'.format(hij_type, hijack))
        else:
            if monitor_event.timestamp < hijack_event.time_started:
                hijack_event.time_started = monitor_event.timestamp

            if monitor_event.timestamp > hijack_event.time_last:
                hijack_event.time_last = monitor_event.timestamp

            hijack_monitors = Monitor.query.filter(
                Monitor.hijack_id.like(hijack_event.id)
            ).all()

            peers_seen = set()
            inf_asns = set()

            # handle inf_asns as if its an type0 hijack
            if hij_type is 'S':
                hij_type = 0
            for monitor in hijack_monitors:
                peers_seen.add(monitor.peer_as)
                inf_asns.update(
                    set(monitor.as_path.split(' ')[:-(hij_type+1)]))

            peers_seen.add(monitor_event.peer_as)
            inf_asns.update(
                set(monitor_event.as_path.split(' ')[:-(hij_type+1)]))
            hijack_event.num_peers_seen = len(peers_seen)
            hijack_event.num_asns_inf = len(inf_asns)
            hijack_id = hijack_event.id

        # Update monitor with new Hijack ID and register possible Hijack event changes
        monitor_event.hijack_id = hijack_id
        monitor_event.handled = True
        db.session.commit()
        #db.session.expunge(monitor_event)

    @staticmethod
    def __remove_prepending(seq):
        last_add = None
        new_seq = []
        for x in seq:
            if last_add != x:
                last_add = x
                new_seq.append(x)

        is_loopy = False
        if len(set(seq)) != len(new_seq):
            is_loopy = True
            #raise Exception('Routing Loop: {}'.format(seq))
        return (new_seq, is_loopy)

    @staticmethod
    def __clean_loops(seq):
        # use inverese direction to clean loops in the path of the traffic
        seq_inv = seq[::-1]
        new_seq_inv = []
        for x in seq_inv:
            if x not in new_seq_inv:
                new_seq_inv.append(x)
            else:
                x_index = new_seq_inv.index(x)
                new_seq_inv = new_seq_inv[:x_index+1]
        return new_seq_inv[::-1]

    @staticmethod
    def __clean_as_path(as_path):
        (clean_as_path, is_loopy) = Detection.__remove_prepending(as_path)
        if is_loopy:
            clean_as_path = Detection.__clean_loops(clean_as_path)
        return as_path

    @exception_handler
    def detect_origin_hijack(self, monitor_event):
        as_path = Detection.__clean_as_path(monitor_event.as_path.split(' '))
        if len(as_path) > 0:
            origin_asn = int(monitor_event.origin_as)
            prefix_node = self.prefix_tree.search_best(
                monitor_event.prefix)
            if prefix_node is not None:
                if origin_asn not in prefix_node.data['origin_asns']:
                    self.commit_hijack(monitor_event, origin_asn, 0)
                    return True
        return False

    @exception_handler
    def detect_type_1_hijack(self, monitor_event):
        as_path = Detection.__clean_as_path(monitor_event.as_path.split(' '))
        if len(as_path) > 1:
            first_neighbor_asn = int(as_path[-2])
            prefix_node = self.prefix_tree.search_best(
                monitor_event.prefix)
            if prefix_node is not None:
                if first_neighbor_asn not in prefix_node.data['neighbors']:
                    self.commit_hijack(monitor_event, first_neighbor_asn, 1)
                    return True
        return False

    @exception_handler
    def detect_subprefix_hijack(self, monitor_event):
        as_path = Detection.__clean_as_path(monitor_event.as_path.split(' '))
        if len(as_path) > 0:
            mon_prefix = ipaddress.ip_network(monitor_event.prefix)
            prefix_node = self.prefix_tree.search_best(
                monitor_event.prefix)
            if prefix_node is not None and prefix_node.prefixlen < mon_prefix.prefixlen:
                self.commit_hijack(monitor_event, -1, 'S')
                return True
        return False


    @exception_handler
    def mark_handled(self, monitor_event):
        monitor_event.handled = True
        db.session.commit()
        #db.session.expunge(monitor_event)
