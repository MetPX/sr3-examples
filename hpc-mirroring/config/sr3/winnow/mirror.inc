
broker amqp://tfeed@localhost

expire 1d

filename None

#on_message msg_rawlog

logdays 2
mdelay 30
flowcb_prepend sarracenia.flowcb.mdelaylatest.MDelayLatest

#cache off
#cache 30
instances 1

permlog 644
durable true
timeCopy true

#debug true
suppress_duplicates 60s

#statehost true
#vip 127.0.0.1

post_broker amqp://tfeed@localhost
post_exchange xs_tfeed_copy_mirror_primary_to_secondary

post_base_url file:/

