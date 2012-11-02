# -*- coding: utf-8 -*-

from decimal import Decimal
from json import dumps, loads
import weakref

import redis
import gevent

from django.core.urlresolvers import reverse
from django.template import loader
from django.conf import settings

from socketio.namespace import BaseNamespace

from .decorators import login_required

from auctions.models import Auction
from auctions.exceptions import *
from auctions import constants

redis_pool = redis.ConnectionPool(host='localhost', port=6379, db=0)

def listener():
    r = redis.StrictRedis(connection_pool=redis_pool)
    r = r.pubsub()
    r.subscribe('chat')
    r.subscribe('auction')
    for message in r.listen():
        if message['type'] != 'message':continue
        print 'got message from redis', message
        data = loads(message['data'])
        pkt = dict(type="event",
                   name=data['event'],
                   args=data['args'])
        if message['channel'] == 'chat':
            klass = ChatNamespace
        elif message['channel'] == 'auction':
            klass = AuctionNamespace

        for ref in klass.instances:
            instance = ref()
            if instance is not None:
                pkt['endpoint'] = instance.ns_name
                instance.socket.send_packet(pkt)

gevent.spawn(listener)


class RedisBroadcast(object):

    def initialize(self):
        self.instances.append(weakref.ref(self))

    def publish(self, event, *args):
        r = redis.Redis()
        msg = {'event':event, 'args':args}
        r.publish(self.channel, dumps(msg))

class ChatNamespace(RedisBroadcast, BaseNamespace):
    instances = []
    channel = 'chat'

    def initialize(self):
        super(ChatNamespace, self).initialize()
        if self.request.user.is_authenticated():
            self.session['username'] = self.request.user.username
            self.session['avatar'] = self.request.user.profile.img_url
        else:
            self.session['username'] = u'guest'
            self.session['avatar'] = '' # pick default avatar

    def on_send_chat_message(self, msg):
        r = redis.Redis(connection_pool=redis_pool)
        if r.sinter('banned_users', self.session['username']):
            return
        self.publish('user_message',self.session['username'],
                    msg[:200], self.session['avatar'] )


class AuctionNamespace(RedisBroadcast, BaseNamespace):
    instances = []
    channel = 'auction'

    @login_required
    def on_fund(self, message):
        try:
            auction = Auction.objects.select_related('item').get(pk=message['auction_pk'])
        except Auction.DoesNotExist:
            return
        member = self.request.user.profile
        amount = Decimal(message['amount'])
        member.pledge(auction, amount)
        member.incr_credits(amount)
        if auction.amount_pleged < auction.item.price:
            self.publish("auction_funded", auction.pk, '%.1f' % auction.amount_pleged,
                        auction.backers, '%.1f' %auction.funded)
        else:
            # do we need to limit auctions number ?
            auction.status = constants.AUCTION_SHOWCASE
            auction.save()
            self.publish("auction_fund_ended", auction.pk, auction.time_left,
             loader.render_to_string('auctions/showcase_box.html',
                     {'auction':auction, 'STATIC_URL':settings.STATIC_URL}))


    @login_required
    def on_bid(self, auction_pk):
        member = self.request.user.profile
        if not auction_pk:
            return
        try:
            auction = Auction.objects.live().get(pk=int(auction_pk))
        except Auction.DoesNotExist:return
        try:
            member.bid(auction)
        except NotEnoughCredits:
            self.emit('NOT_ENOUGH_CREDITS')
        except AlreadyHighestBid:
            self.emit('ALREADY_HIGHEST_BID')
        except AuctionExpired:
            self.emit('AUCTION_EXPIRED')
        else:
            self.publish("auction_bid", auction.pk, auction.time_left,
                         self.request.user.username, member.img_url)
