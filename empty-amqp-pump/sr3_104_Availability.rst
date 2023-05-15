


Using Duplicate Suppression to Optimize an Atom Feed
----------------------------------------------------

When we are querying an ATOM server, we need to parse the returned information in
order to find out if there is new data. If we have a first level downloader,
that downloads the response, then we can compare successive responses, and only
forward new ones.

* remove the datestamping plugin
* have the publisher publish to a private exchange.
* add a Sarra configuration to do the initial download, and republish to the public exchange

* make the republishing condition either by:

  * write an after_work plugin that:

    * compares the new file to the last one downloaded.

      * if they are the same, don't publish.
      * if they are different, publish

  * or configure a second sarra:

      * the first sarra publishes to an intermediate exchange,
      * the second sarra has with *nodupe_ttl 3600* (will only resend once an hour if nothing
    has changed.
      * the second sarra publishes to the public exchange.

With this intermediate processing on a data pump, our initial pump must still do the
gets at high frequency, but we can at least avoid propagating all the repeats of the
same data to our clients.


Duplicate Suppression
---------------------


Checksumming
------------

Winnowing
---------


